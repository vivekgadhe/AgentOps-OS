import { useEffect, useState, type FormEvent } from "react";
import { X } from "lucide-react";

import type { AgentMemory, MemoryCreateRequest, MemoryScope, MemoryType, MemoryUpdateRequest } from "../../../types/memory";

interface MemoryFormProps {
  initial?: AgentMemory | null;
  busy: boolean;
  onClose: () => void;
  onCreate: (payload: MemoryCreateRequest) => Promise<void>;
  onUpdate: (payload: MemoryUpdateRequest) => Promise<void>;
}

export function MemoryForm({ initial = null, busy, onClose, onCreate, onUpdate }: MemoryFormProps) {
  const [memoryType, setMemoryType] = useState<MemoryType>(initial?.memory_type ?? "semantic");
  const [scope, setScope] = useState<MemoryScope>(initial?.memory_scope ?? "user");
  const [agentKey, setAgentKey] = useState(initial?.agent_key ?? "");
  const [content, setContent] = useState(initial?.content ?? "");
  const [importance, setImportance] = useState(String(initial?.importance ?? 0.5));
  const [ttl, setTtl] = useState("");
  const [metadata, setMetadata] = useState(initial ? JSON.stringify(initial.metadata_json, null, 2) : "{}");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMemoryType(initial?.memory_type ?? "semantic");
    setScope(initial?.memory_scope ?? "user");
    setAgentKey(initial?.agent_key ?? "");
    setContent(initial?.content ?? "");
    setImportance(String(initial?.importance ?? 0.5));
    setTtl("");
    setMetadata(initial ? JSON.stringify(initial.metadata_json, null, 2) : "{}");
    setError(null);
  }, [initial]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    const parsedImportance = Number(importance);
    if (!Number.isFinite(parsedImportance) || parsedImportance < 0 || parsedImportance > 1) {
      setError("Importance must be between 0 and 1.");
      return;
    }
    if (!content.trim()) { setError("Memory content is required."); return; }
    const ttlValue = ttl.trim() === "" ? null : Number(ttl);
    if (ttlValue !== null && (!Number.isInteger(ttlValue) || ttlValue < 0 || ttlValue > 3650)) {
      setError("TTL must be an integer between 0 and 3650 days.");
      return;
    }

    if (initial) {
      const payload: MemoryUpdateRequest = {
        ...(content.trim() === initial.content ? {} : { content: content.trim() }),
        importance: parsedImportance,
        ...(ttl.trim() === "" ? {} : { ttl_days: ttlValue }),
      };
      try { await onUpdate(payload); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : "Unable to update memory."); }
      return;
    }

    let metadataJson: Record<string, unknown>;
    try {
      const parsed: unknown = JSON.parse(metadata);
      if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) throw new Error("Metadata must be a JSON object.");
      metadataJson = parsed as Record<string, unknown>;
    } catch (parseError) {
      setError(parseError instanceof Error ? parseError.message : "Metadata must be valid JSON.");
      return;
    }
    if (scope === "agent" && !/^[a-z][a-z0-9_]{0,99}$/.test(agentKey.trim())) {
      setError("Agent key must start with a lowercase letter and contain only lowercase letters, numbers and underscores.");
      return;
    }
    const payload: MemoryCreateRequest = {
      memory_type: memoryType,
      memory_scope: scope,
      ...(scope === "agent" ? { agent_key: agentKey.trim() } : {}),
      content: content.trim(),
      importance: parsedImportance,
      ttl_days: ttlValue,
      metadata_json: metadataJson,
    };
    try { await onCreate(payload); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : "Unable to create memory."); }
  };

  return (
    <div className="p3-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !busy) onClose(); }}>
      <section className="p3-modal-card" role="dialog" aria-modal="true" aria-labelledby="memory-form-title">
        <div className="p3-card-heading"><div><span className="p3-eyebrow">PERSISTENT AGENT MEMORY</span><h2 id="memory-form-title">{initial ? "Edit memory" : "Create memory"}</h2></div><button type="button" className="p3-icon-button" disabled={busy} onClick={onClose} aria-label="Close"><X size={17} /></button></div>
        <form className="p3-memory-form" onSubmit={(event) => void submit(event)}>
          {!initial && <div className="p3-form-grid"><label><span>Memory type</span><select value={memoryType} onChange={(event) => setMemoryType(event.target.value as MemoryType)}><option value="episodic">Episodic</option><option value="semantic">Semantic</option></select></label><label><span>Memory scope</span><select value={scope} onChange={(event) => setScope(event.target.value as MemoryScope)}><option value="user">User</option><option value="agent">Agent</option></select></label></div>}
          {!initial && scope === "agent" && <label><span>Agent key</span><input value={agentKey} onChange={(event) => setAgentKey(event.target.value)} placeholder="analysis_agent" maxLength={100} /></label>}
          <label><span>Memory content</span><textarea rows={5} value={content} onChange={(event) => setContent(event.target.value)} maxLength={5000} placeholder="Write the fact, preference or event to remember…" /></label>
          <div className="p3-form-grid"><label><span>Importance (0–1)</span><input type="number" min="0" max="1" step="0.05" value={importance} onChange={(event) => setImportance(event.target.value)} /></label><label><span>TTL days</span><input type="number" min="0" max="3650" step="1" value={ttl} onChange={(event) => setTtl(event.target.value)} placeholder={initial ? "Unchanged" : "Configured default"} /></label></div>
          {!initial && <label><span>Metadata JSON</span><textarea className="p3-mono-input" rows={3} value={metadata} onChange={(event) => setMetadata(event.target.value)} /></label>}
          <p className="p3-muted-note">On create, blank TTL uses the configured default. On edit, blank leaves expiry unchanged; set TTL to 0 to remove expiration.</p>
          {error && <p className="p3-inline-error" role="alert">{error}</p>}
          <div className="p3-modal-actions"><button type="button" className="p3-secondary-button" disabled={busy} onClick={onClose}>Cancel</button><button type="submit" className="p3-primary-button" disabled={busy}>{busy ? <span className="p3-spinner" /> : null}{busy ? "Saving…" : initial ? "Save changes" : "Create memory"}</button></div>
        </form>
      </section>
    </div>
  );
}
