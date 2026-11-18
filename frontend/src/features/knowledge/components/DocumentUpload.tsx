import { useRef, useState } from "react";
import { FileUp, UploadCloud } from "lucide-react";

interface DocumentUploadProps {
  busy: boolean;
  disabled?: boolean;
  onUpload: (file: File) => Promise<void>;
}

const ACCEPTED_EXTENSIONS = [".pdf", ".txt", ".md"];

export function DocumentUpload({ busy, disabled = false, onUpload }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chooseFile = (candidate?: File) => {
    if (!candidate) return;
    const extension = candidate.name.slice(candidate.name.lastIndexOf(".")).toLowerCase();
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      setFile(null);
      setError("Choose a PDF, TXT or Markdown (.md) file.");
      return;
    }
    setError(null);
    setFile(candidate);
  };

  const submit = async () => {
    if (!file) return;
    setError(null);
    try {
      await onUpload(file);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Document upload failed.");
    }
  };

  return (
    <section className="p3-card p3-upload-card">
      <div className="p3-card-heading">
        <div><span className="p3-eyebrow">ADD TO YOUR KNOWLEDGE BASE</span><h2>Upload a document</h2></div>
        <span className="p3-icon-tile violet"><FileUp size={19} /></span>
      </div>
      <button
        type="button"
        className={`p3-dropzone${dragging ? " is-dragging" : ""}`}
        disabled={disabled || busy}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => { event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]); }}
      >
        <span className="p3-dropzone-icon"><UploadCloud size={22} /></span>
        <strong>{file ? file.name : "Drop a document here or browse files"}</strong>
        <small>PDF, TXT and Markdown files · Owner-scoped indexing</small>
      </button>
      <input ref={inputRef} hidden type="file" accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown" onChange={(event) => chooseFile(event.target.files?.[0])} />
      {error && <p className="p3-inline-error" role="alert">{error}</p>}
      {disabled ? (
        <p className="p3-muted-note">Your account can search existing documents. An administrator or operator role is required to upload or delete documents.</p>
      ) : (
        <div className="p3-upload-footer">
          <span className="p3-muted-note">Files are indexed using the configured local embedding service.</span>
          <button type="button" className="p3-primary-button" disabled={!file || busy} onClick={() => void submit()}>
            {busy ? <span className="p3-spinner" /> : <UploadCloud size={15} />}{busy ? "Uploading…" : "Upload & index"}
          </button>
        </div>
      )}
    </section>
  );
}
