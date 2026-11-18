import { Brain, Clock3, RefreshCw } from "lucide-react";

import type { AgentMemory } from "../../../types/memory";

interface MemoryListProps {
  memories: AgentMemory[];
  selectedId: string | null;
  loading: boolean;
  onSelect: (memory: AgentMemory) => void;
  onRefresh: () => void;
}

export function MemoryList({ memories, selectedId, loading, onSelect, onRefresh }: MemoryListProps) {
  return (
    <section className="p3-card p3-memory-list-card">
      <div className="p3-card-heading"><div><span className="p3-eyebrow">PERSISTENT MEMORY</span><h2>Stored memories <span className="p3-count-pill">{memories.length}</span></h2></div><button type="button" className="p3-icon-button" onClick={onRefresh} aria-label="Refresh memories"><RefreshCw size={15} /></button></div>
      {loading ? <div className="p3-loading-state"><span className="p3-spinner dark" />Loading memories…</div> : memories.length === 0 ? <div className="p3-empty-state"><span className="p3-empty-icon"><Brain size={22} /></span><strong>No active memories</strong><p>Create a user or agent memory, or use semantic search to retrieve relevant context.</p></div> : (
        <div className="p3-memory-list">{memories.map((memory) => <button type="button" key={memory.id} className={`p3-memory-row${selectedId === memory.id ? " is-selected" : ""}`} onClick={() => onSelect(memory)}><span className={`p3-memory-type-icon ${memory.memory_type}`}><Brain size={17} /></span><span className="p3-memory-row-copy"><strong>{memory.content.slice(0, 92)}{memory.content.length > 92 ? "…" : ""}</strong><small>{memory.memory_type} · {memory.memory_scope === "agent" ? memory.agent_key : "user scope"}</small></span><span className="p3-memory-time"><Clock3 size={11} />{new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(memory.updated_at))}</span></button>)}</div>
      )}
    </section>
  );
}
