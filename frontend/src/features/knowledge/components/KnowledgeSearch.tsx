import { Search, Sparkles } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { KnowledgeCitation, KnowledgeSearchResponse } from "../../../types/knowledge";

interface KnowledgeSearchProps {
  searching: boolean;
  result: KnowledgeSearchResponse | null;
  error: string | null;
  onSearch: (query: string, topK: number) => Promise<void>;
}

function CitationCard({ citation }: { citation: KnowledgeCitation }) {
  return (
    <article className="p3-citation-card">
      <div className="p3-citation-top"><span className="p3-source-chip">{citation.source_id}</span><strong>{citation.filename}</strong><span className="p3-similarity">{Math.round(citation.similarity * 100)}% similarity</span></div>
      <p>{citation.content}</p>
      <small>Chunk {citation.chunk_index + 1}{citation.page_number ? ` · Page ${citation.page_number}` : ""}</small>
    </article>
  );
}

export function KnowledgeSearch({ searching, result, error, onSearch }: KnowledgeSearchProps) {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState("5");
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (query.trim()) void onSearch(query.trim(), Number(topK));
  };

  return (
    <section className="p3-card p3-search-workspace">
      <div className="p3-card-heading"><div><span className="p3-eyebrow">SEMANTIC RETRIEVAL</span><h2>Search your knowledge base</h2><p>Find relevant passages across documents you own.</p></div><span className="p3-icon-tile violet"><Search size={19} /></span></div>
      <form className="p3-search-form" onSubmit={submit}>
        <label className="p3-field-label" htmlFor="knowledge-query">What are you looking for?</label>
        <textarea id="knowledge-query" rows={3} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask a question or describe the information you need…" maxLength={10_000} />
        <div className="p3-form-toolbar"><label className="p3-compact-field">Results <select value={topK} onChange={(event) => setTopK(event.target.value)}><option value="3">3 results</option><option value="5">5 results</option><option value="10">10 results</option><option value="20">20 results</option></select></label><button className="p3-primary-button" type="submit" disabled={!query.trim() || searching}>{searching ? <span className="p3-spinner" /> : <Sparkles size={15} />}{searching ? "Searching…" : "Search documents"}</button></div>
      </form>
      {error && <p className="p3-inline-error" role="alert">{error}</p>}
      {result && <div className="p3-search-results"><div className="p3-results-heading"><strong>{result.results.length} relevant passage{result.results.length === 1 ? "" : "s"}</strong><span>for “{result.query}”</span></div>{result.results.length === 0 ? <div className="p3-empty-state compact"><strong>No matching passages</strong><p>Try a different phrase or upload more documents.</p></div> : result.results.map((citation) => <CitationCard key={`${citation.document_id}-${citation.chunk_index}`} citation={citation} />)}</div>}
      {!result && !searching && <div className="p3-search-hint"><Sparkles size={17} /><span>Semantic search uses your configured local embedding model and only retrieves passages from your own documents.</span></div>}
    </section>
  );
}
