import { useMemo, useState } from "react";
import { Database, FileSearch, Files, Layers3 } from "lucide-react";

import { useAuth } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../../lib/api-error";
import type { KnowledgeDocument, KnowledgeSearchResponse } from "../../types/knowledge";
import { DocumentDetails } from "./components/DocumentDetails";
import { DocumentList } from "./components/DocumentList";
import { DocumentUpload } from "./components/DocumentUpload";
import { KnowledgeSearch } from "./components/KnowledgeSearch";
import { useDeleteKnowledgeDocument, useKnowledgeDocuments, useKnowledgeSearch, useUploadKnowledgeDocument } from "./hooks/useKnowledge";

type KnowledgeTab = "documents" | "search";

export function KnowledgePage() {
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "operator";
  const [tab, setTab] = useState<KnowledgeTab>("documents");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [searchResult, setSearchResult] = useState<KnowledgeSearchResponse | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  const documentsQuery = useKnowledgeDocuments();
  const uploadMutation = useUploadKnowledgeDocument();
  const deleteMutation = useDeleteKnowledgeDocument();
  const searchMutation = useKnowledgeSearch();

  const documents = documentsQuery.data ?? [];
  const selectedDocument = useMemo<KnowledgeDocument | null>(
    () => documents.find((document) => document.id === selectedId) ?? null,
    [documents, selectedId],
  );
  const totalChunks = documents.reduce((sum, document) => sum + document.chunk_count, 0);
  const totalPages = documents.reduce((sum, document) => sum + document.page_count, 0);

  const upload = async (file: File) => {
    setNotice(null);
    try {
      await uploadMutation.mutateAsync(file);
      setNotice(`${file.name} was uploaded and indexed successfully.`);
    } catch (error) {
      throw new Error(getApiErrorMessage(error, "Unable to upload this document. Check the embedding service and file type."));
    }
  };

  const remove = async (document: KnowledgeDocument) => {
    if (!window.confirm(`Delete “${document.filename}” and its indexed chunks? This cannot be undone.`)) return;
    setNotice(null);
    try {
      await deleteMutation.mutateAsync(document.id);
      if (selectedId === document.id) setSelectedId(null);
      setNotice(`${document.filename} was deleted.`);
    } catch (error) {
      setNotice(getApiErrorMessage(error, "Unable to delete this document."));
    }
  };

  const search = async (query: string, topK: number) => {
    setSearchError(null);
    setSearchResult(null);
    try {
      const result = await searchMutation.mutateAsync({ query, top_k: topK });
      setSearchResult(result);
    } catch (error) {
      setSearchError(getApiErrorMessage(error, "Knowledge search failed. Check the local embedding service and try again."));
    }
  };

  return (
    <section className="p3-page phase2-page">
      <header className="p3-page-heading">
        <div><span className="p3-eyebrow"><Database size={13} /> KNOWLEDGE WORKSPACE</span><h1>Knowledge Management</h1><p>Upload, index and retrieve information from your own documents.</p></div>
        <div className="p3-heading-status"><span className="p3-status-dot" /> Owner-scoped library</div>
      </header>

      <div className="p3-stat-strip">
        <div className="p3-mini-stat"><span className="p3-mini-stat-icon violet"><Files size={17} /></span><span><strong>{documents.length}</strong><small>Documents</small></span></div>
        <div className="p3-mini-stat"><span className="p3-mini-stat-icon cyan"><Layers3 size={17} /></span><span><strong>{totalChunks}</strong><small>Indexed chunks</small></span></div>
        <div className="p3-mini-stat"><span className="p3-mini-stat-icon blue"><FileSearch size={17} /></span><span><strong>{totalPages}</strong><small>PDF pages</small></span></div>
      </div>

      <div className="p3-tabs" role="tablist" aria-label="Knowledge tools">
        <button type="button" role="tab" aria-selected={tab === "documents"} className={tab === "documents" ? "is-active" : ""} onClick={() => setTab("documents")}>Documents</button>
        <button type="button" role="tab" aria-selected={tab === "search"} className={tab === "search" ? "is-active" : ""} onClick={() => setTab("search")}>Semantic search</button>
      </div>

      {notice && <div className="p3-success-banner" role="status">{notice}</div>}
      {documentsQuery.isError && <div className="p3-inline-error" role="alert">{getApiErrorMessage(documentsQuery.error, "Unable to load your knowledge documents.")}</div>}

      {tab === "documents" ? (
        <div className="p3-knowledge-grid">
          <div className="p3-knowledge-main">
            <DocumentUpload busy={uploadMutation.isPending} disabled={!canManage} onUpload={upload} />
            <DocumentList documents={documents} selectedId={selectedId} loading={documentsQuery.isLoading} deletingId={deleteMutation.isPending ? (deleteMutation.variables ?? null) : null} canManage={canManage} onSelect={(document) => setSelectedId(document.id)} onDelete={(document) => void remove(document)} onRefresh={() => void documentsQuery.refetch()} />
          </div>
          <DocumentDetails document={selectedDocument} />
        </div>
      ) : (
        <KnowledgeSearch searching={searchMutation.isPending} result={searchResult} error={searchError} onSearch={search} />
      )}
      <p className="p3-page-footnote">Supported file types: PDF, TXT and Markdown. Upload, semantic search and agent retrieval use the backend's configured local embedding service.</p>
    </section>
  );
}
