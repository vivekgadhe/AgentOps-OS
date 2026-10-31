"""Unit tests for document extraction and chunking."""

from types import SimpleNamespace

import pytest

import agentops.services.document_processing as processing
from agentops.services.document_processing import (
    DocumentPage,
    DocumentProcessingError,
    chunk_document_pages,
    extract_document_pages,
    media_type_for_filename,
    sanitize_filename,
)


def test_text_file_is_decoded_and_normalized() -> None:
    media_type, pages = extract_document_pages("notes.txt", b"one\r\ntwo\rthree")
    assert media_type == "text/plain"
    assert pages == [DocumentPage(page_number=None, text="one\ntwo\nthree")]


def test_markdown_file_is_supported() -> None:
    media_type, pages = extract_document_pages("guide.md", b"# Heading\nBody")
    assert media_type == "text/markdown"
    assert "# Heading" in pages[0].text


def test_unsupported_extension_is_rejected() -> None:
    with pytest.raises(DocumentProcessingError, match="Only PDF, TXT, and Markdown"):
        media_type_for_filename("image.png")


def test_invalid_utf8_is_rejected() -> None:
    with pytest.raises(DocumentProcessingError, match="UTF-8"):
        extract_document_pages("notes.txt", b"\xff\xfe")


def test_empty_text_is_rejected() -> None:
    with pytest.raises(DocumentProcessingError, match="empty"):
        extract_document_pages("notes.txt", b"  \n  ")


def test_filename_path_components_are_removed() -> None:
    assert sanitize_filename("..\\folder\\notes.txt") == "notes.txt"


def test_pdf_extraction_preserves_page_numbers(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_reader = SimpleNamespace(
        is_encrypted=False,
        pages=[
            SimpleNamespace(extract_text=lambda: "First page"),
            SimpleNamespace(extract_text=lambda: "Second page"),
        ],
    )
    monkeypatch.setattr(processing, "PdfReader", lambda *_args, **_kwargs: fake_reader)
    media_type, pages = extract_document_pages("guide.pdf", b"fake-pdf")
    assert media_type == "application/pdf"
    assert [page.page_number for page in pages] == [1, 2]


def test_pdf_without_extractable_text_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_reader = SimpleNamespace(
        is_encrypted=False,
        pages=[SimpleNamespace(extract_text=lambda: "")],
    )
    monkeypatch.setattr(processing, "PdfReader", lambda *_args, **_kwargs: fake_reader)
    with pytest.raises(DocumentProcessingError, match="no extractable text"):
        extract_document_pages("scan.pdf", b"fake-pdf")


def test_chunking_respects_page_boundaries_and_overlap() -> None:
    pages = [
        DocumentPage(page_number=1, text="alpha " * 100),
        DocumentPage(page_number=2, text="beta " * 100),
    ]
    chunks = chunk_document_pages(pages, chunk_size=100, overlap=20)
    assert len(chunks) > 2
    assert {chunk.page_number for chunk in chunks} == {1, 2}
    assert all(len(chunk.content) <= 100 for chunk in chunks)


def test_chunking_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError, match="smaller than"):
        chunk_document_pages([DocumentPage(None, "text")], chunk_size=10, overlap=10)
