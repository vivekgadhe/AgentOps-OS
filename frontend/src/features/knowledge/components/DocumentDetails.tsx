import { CalendarClock, Copy, FileText, Hash, Layers3 } from "lucide-react";

import type { KnowledgeDocument } from "../../../types/knowledge";

interface DocumentDetailsProps { document: KnowledgeDocument | null; }

export function DocumentDetails({ document }: DocumentDetailsProps) {
  if (!document) {
    return <aside className="p3-card p3-detail-card"><div className="p3-detail-placeholder"><FileText size={24} /><strong>Select a document</strong><span>Choose a document from your library to inspect its indexing metadata.</span></div></aside>;
  }

  const copyHash = async () => {
    try { await navigator.clipboard.writeText(document.sha256); } catch { /* Clipboard access may be unavailable in insecure contexts. */ }
  };

  return (
    <aside className="p3-card p3-detail-card">
      <div className="p3-card-heading"><div><span className="p3-eyebrow">DOCUMENT DETAILS</span><h2>Index information</h2></div><span className="p3-icon-tile cyan"><FileText size={18} /></span></div>
      <div className="p3-detail-file"><span className="p3-document-icon large"><FileText size={21} /></span><strong>{document.filename}</strong><small>{document.media_type}</small></div>
      <div className="p3-detail-metrics">
        <div><Layers3 size={16} /><strong>{document.chunk_count}</strong><span>Indexed chunks</span></div>
        <div><FileText size={16} /><strong>{document.page_count}</strong><span>Pages</span></div>
      </div>
      <dl className="p3-metadata-list">
        <div><dt><CalendarClock size={13} /> Added</dt><dd>{new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(document.created_at))}</dd></div>
        <div className="p3-hash-row"><dt><Hash size={13} /> SHA-256</dt><dd><code>{document.sha256.slice(0, 18)}…</code><button type="button" className="p3-copy-button" onClick={() => void copyHash()} aria-label="Copy SHA-256"><Copy size={12} /></button></dd></div>
      </dl>
      <p className="p3-muted-note">Document metadata is returned by the authenticated knowledge API. File contents and embeddings are not exposed in this details panel.</p>
    </aside>
  );
}
