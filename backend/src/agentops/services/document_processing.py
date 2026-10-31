"""Safe extraction and deterministic chunking for supported documents."""

from dataclasses import dataclass
from io import BytesIO
from typing import Final

from pypdf import PdfReader

MAX_FILENAME_LENGTH: Final[int] = 255

SUPPORTED_MEDIA_TYPES: Final[dict[str, str]] = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
}


class DocumentProcessingError(ValueError):
    """Raised when an uploaded document cannot be safely processed."""


@dataclass(frozen=True, slots=True)
class DocumentPage:
    """Extracted text and optional one-based PDF page number."""

    page_number: int | None
    text: str


@dataclass(frozen=True, slots=True)
class TextChunk:
    """A deterministic, source-locatable text chunk."""

    chunk_index: int
    page_number: int | None
    content: str
    start_char: int
    end_char: int


def sanitize_filename(filename: str) -> str:
    """Keep a basename only and reject blank/control-character filenames."""

    basename = filename.replace("\\", "/").split("/")[-1].strip()

    if not basename or basename in {".", ".."}:
        raise DocumentProcessingError("A valid filename is required.")

    if any(ord(char) < 32 or ord(char) == 127 for char in basename):
        raise DocumentProcessingError("Filename contains unsupported characters.")

    if len(basename) > MAX_FILENAME_LENGTH:
        raise DocumentProcessingError("Filename exceeds 255 characters.")

    return basename


def media_type_for_filename(filename: str) -> str:
    """Resolve a supported media type from the filename extension."""

    extension = "." + filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""

    try:
        return SUPPORTED_MEDIA_TYPES[extension]
    except KeyError as exc:
        raise DocumentProcessingError(
            "Only PDF, TXT, and Markdown documents are supported."
        ) from exc


def extract_document_pages(
    filename: str,
    content: bytes,
    *,
    max_pdf_pages: int = 200,
) -> tuple[str, list[DocumentPage]]:
    """Extract searchable text from supported files."""

    safe_filename = sanitize_filename(filename)
    media_type = media_type_for_filename(safe_filename)

    if not content:
        raise DocumentProcessingError("The uploaded document is empty.")

    if media_type in {"text/plain", "text/markdown"}:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentProcessingError("Text documents must use UTF-8 encoding.") from exc

        if "\x00" in text:
            raise DocumentProcessingError("Text document contains a null character.")

        normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()

        if not normalized:
            raise DocumentProcessingError(
                "The uploaded text document is empty or contains no extractable text."
            )

        return media_type, [
            DocumentPage(
                page_number=None,
                text=normalized,
            )
        ]

    try:
        reader = PdfReader(BytesIO(content), strict=False)

        if reader.is_encrypted:
            raise DocumentProcessingError("Encrypted PDFs are not supported.")

        page_count = len(reader.pages)

        if page_count > max_pdf_pages:
            raise DocumentProcessingError(f"PDF exceeds the {max_pdf_pages}-page processing limit.")

        pages: list[DocumentPage] = []

        for index, page in enumerate(reader.pages, start=1):
            extracted = page.extract_text() or ""
            normalized = extracted.replace("\x00", "").strip()

            pages.append(
                DocumentPage(
                    page_number=index,
                    text=normalized,
                )
            )

    except DocumentProcessingError:
        raise
    except Exception as exc:
        raise DocumentProcessingError("The PDF could not be read.") from exc

    # A PDF can contain pages but still have no extractable text.
    if not pages or not any(page.text.strip() for page in pages):
        raise DocumentProcessingError(
            "The PDF has no extractable text. Scanned PDFs require OCR, which is not enabled."
        )

    return media_type, pages


def chunk_document_pages(
    pages: list[DocumentPage],
    *,
    chunk_size: int = 1200,
    overlap: int = 200,
    max_chunks: int = 5000,
) -> list[TextChunk]:
    """Split pages into overlapping chunks without crossing page citations."""

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size.")

    if max_chunks < 1:
        raise ValueError("max_chunks must be positive.")

    chunks: list[TextChunk] = []

    for page in pages:
        text = page.text.strip()
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            if end < len(text):
                boundary = text.rfind(
                    " ",
                    start + chunk_size // 2,
                    end,
                )

                if boundary > start:
                    end = boundary

            original_piece = text[start:end]
            piece = original_piece.strip()

            if piece:
                left_trim = len(original_piece) - len(original_piece.lstrip())

                right_trim = len(original_piece) - len(original_piece.rstrip())

                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        page_number=page.page_number,
                        content=piece,
                        start_char=start + left_trim,
                        end_char=end - right_trim,
                    )
                )

                if len(chunks) > max_chunks:
                    raise DocumentProcessingError(
                        f"Document exceeds the {max_chunks}-chunk processing limit."
                    )

            if end >= len(text):
                break

            next_start = max(start + 1, end - overlap)
            start = next_start

    if not chunks:
        raise DocumentProcessingError("No non-empty text chunks were produced.")

    return chunks
