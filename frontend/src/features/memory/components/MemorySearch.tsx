import { Search, Sparkles } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { MemorySearchRequest, MemorySearchResponse, MemoryType } from "../../../types/memory";

interface MemorySearchProps {
  busy: boolean;
  result: MemorySearchResponse | null;
  error: string | null;
  onSearch: (payload: MemorySearchRequest) => Promise<void>;
  onSelectMemory: (memoryId: string) => void;
}

export function MemorySearch({ busy, result, error, onSearch, onSelectMemory }: MemorySearchProps) {
  const [query, setQuery] = useState("");
  const [memoryType, setMemoryType] = useState<MemoryType | "">("");
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return;
    void onSearch({ query: query.trim(), top_k: 5, min_similarity: 0, ...(memoryType ? { memory_type: memoryType } : {}) });
  };

  return (
    <section className="p3-card p3-memory-search-card">
      <div className="p3-card-heading"><div><span className="p3-eyebrow">SEMANTIC MEMORY RETRIEVAL</span><h2>Find relevant memories</h2><p>Search active memories visible to your account using the configured local embedding model.</p></div><span className="p3-icon-tile violet"><Search size={18} /></span></div>
      <form className="p3-search-form" onSubmit={submit}>
        <label className="p3-field-label" htmlFor="memory-search-query">Search query</label>
        <div className="p3-memory-search-row"><input id="memory-search-query" value={query} onChange={(event) => setQuery(event.target.value)} maxLength={2_000} placeholder="Search what an agent or user should remember…" /><select value={memoryType} onChange={(event) => setMemoryType(event.target.value as MemoryType | "")} aria-label="Filter memory type"><option value="">All types</option><option value="episodic">Episodic</option><option value="semantic">Semantic</option></select><button className="p3-primary-button" type="submit" disabled={!query.trim() || busy}>{busy ? <span className="p3-spinner" /> : <Sparkles size={14} />}{busy ? "Searching…" : "Search"}</button></div>
      </form>
      {error && <p className="p3-inline-error" role="alert">{error}</p>}
      {result && <div className="p3-memory-search-result"><strong>{result.results.length} matching memories</strong>{result.results.length === 0 ? <p className="p3-muted-note">No relevant memories found. Try another query.</p> : result.results.map((hit) => <article className="p3-memory-hit" key={hit.memory.id}><button type="button" className="p3-memory-hit-open" onClick={() => onSelectMemory(hit.memory.id)}><div><span className="p3-source-chip">{hit.memory.memory_type}</span><strong>{hit.memory.memory_scope === "agent" ? hit.memory.agent_key : "User memory"}</strong></div><p>{hit.memory.content}</p><small>Similarity {Math.round(hit.similarity * 100)}% · Relevance {hit.relevance_score.toFixed(3)}</small></button></article>)}</div>}
    </section>
  );
}
