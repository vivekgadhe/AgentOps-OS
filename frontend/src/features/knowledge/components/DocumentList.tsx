import { FileText, RefreshCw, Trash2 } from "lucide-react";

import type { KnowledgeDocument } from "../../../types/knowledge";

interface DocumentListProps {
  documents: KnowledgeDocument[];
  selectedId: string | null;
  loading: boolean;
  deletingId: string | null;
  canManage: boolean;
  onSelect: (document: KnowledgeDocument) => void;
  onDelete: (document: KnowledgeDocument) => void;
  onRefresh: () => void;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function DocumentList({ documents, selectedId, loading, deletingId, canManage, onSelect, onDelete, onRefresh }: DocumentListProps) {
  return (
    <section className="p3-card p3-document-list-card">
      <div className="p3-card-heading">
        <div><span className="p3-eyebrow">YOUR LIBRARY</span><h2>Knowledge documents <span className="p3-count-pill">{documents.length}</span></h2></div>
        <button type="button" className="p3-icon-button" onClick={onRefresh} aria-label="Refresh documents" title="Refresh documents"><RefreshCw size={16} /></button>
      </div>
      {loading ? <div className="p3-loading-state"><span className="p3-spinner dark" />Loading your documents…</div> : documents.length === 0 ? (
        <div className="p3-empty-state"><span className="p3-empty-icon"><FileText size={23} /></span><strong>No documents yet</strong><p>Upload a PDF, text or Markdown file to build your searchable knowledge base.</p></div>
      ) : (
        <div className="p3-document-list">
          {documents.map((document) => (
            <div key={document.id} className={`p3-document-row${selectedId === document.id ? " is-selected" : ""}`}>
              <button type="button" className="p3-document-main" onClick={() => onSelect(document)}>
                <span className="p3-document-icon"><FileText size={18} /></span>
                <span className="p3-document-copy"><strong title={document.filename}>{document.filename}</strong><small>{document.chunk_count} chunks · {document.page_count > 0 ? `${document.page_count} pages` : "Text document"} · {formatDate(document.created_at)}</small></span>
                <span className="p3-indexed-badge">Indexed</span>
              </button>
              {canManage && <button type="button" className="p3-danger-icon-button" disabled={deletingId === document.id} onClick={() => onDelete(document)} aria-label={`Delete ${document.filename}`} title="Delete document">{deletingId === document.id ? <span className="p3-spinner dark" /> : <Trash2 size={15} />}</button>}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
