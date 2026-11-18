import { CalendarClock, Clock3, Pencil, Trash2 } from "lucide-react";

import type { AgentMemory } from "../../../types/memory";

interface MemoryDetailsProps {
  memory: AgentMemory | null;
  loading: boolean;
  canManage: boolean;
  onEdit: (memory: AgentMemory) => void;
  onDelete: (memory: AgentMemory) => void;
}

function formatDate(value: string | null): string {
  return value ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Never";
}

export function MemoryDetails({ memory, loading, canManage, onEdit, onDelete }: MemoryDetailsProps) {
  if (loading) return <aside className="p3-card p3-memory-detail"><div className="p3-loading-state"><span className="p3-spinner dark" />Loading memory details…</div></aside>;
  if (!memory) return <aside className="p3-card p3-memory-detail"><div className="p3-detail-placeholder"><Clock3 size={23} /><strong>Select a memory</strong><span>Choose a memory to inspect its content, scope, provenance and expiration.</span></div></aside>;

  return (
    <aside className="p3-card p3-memory-detail">
      <div className="p3-card-heading"><div><span className="p3-eyebrow">MEMORY RECORD</span><h2>Memory details</h2></div><span className="p3-icon-tile cyan"><Clock3 size={18} /></span></div>
      <div className="p3-memory-badges"><span className="p3-source-chip">{memory.memory_type}</span><span className="p3-source-chip">{memory.memory_scope} scope</span><span className="p3-source-chip">{memory.source_type} source</span></div>
      <div className="p3-memory-content">{memory.content}</div>
      <div className="p3-memory-importance"><span>Importance</span><strong>{Math.round(memory.importance * 100)}%</strong><div><i style={{ width: `${memory.importance * 100}%` }} /></div></div>
      <dl className="p3-metadata-list">
        {memory.agent_key && <div><dt>Agent key</dt><dd>{memory.agent_key}</dd></div>}
        <div><dt>Confidence</dt><dd>{Math.round(memory.confidence * 100)}%</dd></div>
        <div><dt>Embedding model</dt><dd>{memory.embedding_model}</dd></div>
        <div><dt><CalendarClock size={13} /> Created</dt><dd>{formatDate(memory.created_at)}</dd></div>
        <div><dt>Last accessed</dt><dd>{formatDate(memory.last_accessed_at)}</dd></div>
        <div><dt>Expires</dt><dd>{formatDate(memory.expires_at)}</dd></div>
        {memory.source_workflow_run_id && <div><dt>Source workflow</dt><dd><code>{memory.source_workflow_run_id.slice(0, 12)}…</code></dd></div>}
      </dl>
      {Object.keys(memory.metadata_json).length > 0 && <details className="p3-agent-output"><summary>Metadata JSON</summary><pre>{JSON.stringify(memory.metadata_json, null, 2)}</pre></details>}
      {canManage && <div className="p3-memory-detail-actions"><button type="button" className="p3-secondary-button" onClick={() => onEdit(memory)}><Pencil size={14} /> Edit memory</button><button type="button" className="p3-danger-button" onClick={() => onDelete(memory)}><Trash2 size={14} /> Delete</button></div>}
    </aside>
  );
}
