import { useMemo, useState } from "react";
import { Archive, Brain, Plus, Search } from "lucide-react";

import { useAuth } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../../lib/api-error";
import type { AgentMemory, MemoryCreateRequest, MemorySearchRequest, MemorySearchResponse, MemoryScope, MemoryType, MemoryUpdateRequest } from "../../types/memory";
import { MemoryDetails } from "./components/MemoryDetails";
import { MemoryForm } from "./components/MemoryForm";
import { MemoryList } from "./components/MemoryList";
import { MemorySearch } from "./components/MemorySearch";
import { useCreateMemory, useDeleteMemory, useMemories, useMemoryDetails, usePurgeExpiredMemories, useSearchMemories, useUpdateMemory } from "./hooks/useMemory";

export function MemoryPage() {
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "operator";
  const [memoryType, setMemoryType] = useState<MemoryType | "">("");
  const [scope, setScope] = useState<MemoryScope | "">("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingMemory, setEditingMemory] = useState<AgentMemory | null>(null);
  const [searchResult, setSearchResult] = useState<MemorySearchResponse | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const params = useMemo(() => ({ ...(memoryType ? { memory_type: memoryType } : {}), ...(scope ? { memory_scope: scope } : {}), limit: 100 }), [memoryType, scope]);
  const memoriesQuery = useMemories(params);
  const detailsQuery = useMemoryDetails(selectedId);
  const createMutation = useCreateMemory();
  const updateMutation = useUpdateMemory();
  const deleteMutation = useDeleteMemory();
  const searchMutation = useSearchMemories();
  const purgeMutation = usePurgeExpiredMemories();
  const memories = memoriesQuery.data ?? [];
  const detailMemory = detailsQuery.data ?? memories.find((memory) => memory.id === selectedId) ?? null;

  const openCreate = () => { setEditingMemory(null); setFormOpen(true); };
  const openEdit = (memory: AgentMemory) => { setEditingMemory(memory); setFormOpen(true); };

  const create = async (payload: MemoryCreateRequest) => {
    try {
      const created = await createMutation.mutateAsync(payload);
      setSelectedId(created.id);
      setSearchResult(null);
      setNotice("Memory created and embedded successfully.");
      setFormOpen(false);
    } catch (error) {
      throw new Error(getApiErrorMessage(error, "Unable to create memory. Check that the local embedding service is running."));
    }
  };

  const update = async (payload: MemoryUpdateRequest) => {
    if (!editingMemory) return;
    try {
      await updateMutation.mutateAsync({ id: editingMemory.id, payload });
      setNotice("Memory updated successfully.");
      setFormOpen(false);
    } catch (error) {
      throw new Error(getApiErrorMessage(error, "Unable to update memory. Content changes require the local embedding service."));
    }
  };

  const remove = async (memory: AgentMemory) => {
    if (!window.confirm("Delete this memory permanently? This cannot be undone.")) return;
    try {
      await deleteMutation.mutateAsync(memory.id);
      if (selectedId === memory.id) setSelectedId(null);
      setNotice("Memory deleted.");
    } catch (error) {
      setNotice(getApiErrorMessage(error, "Unable to delete memory."));
    }
  };

  const search = async (payload: MemorySearchRequest) => {
    setSearchError(null);
    setSearchResult(null);
    try {
      setSearchResult(await searchMutation.mutateAsync(payload));
    } catch (error) {
      setSearchError(getApiErrorMessage(error, "Memory search failed. Check the local embedding service and try again."));
    }
  };

  const purgeExpired = async () => {
    if (!window.confirm("Permanently delete all expired memories owned by your account?")) return;
    try {
      const result = await purgeMutation.mutateAsync();
      setNotice(`${result.deleted_count} expired memor${result.deleted_count === 1 ? "y was" : "ies were"} purged.`);
    } catch (error) {
      setNotice(getApiErrorMessage(error, "Unable to purge expired memories."));
    }
  };

  return (
    <section className="p3-page phase2-page">
      <header className="p3-page-heading">
        <div><span className="p3-eyebrow"><Brain size={13} /> PERSISTENT CONTEXT</span><h1>Agent Memory</h1><p>Manage the facts and context that are available to your agents over time.</p></div>
        <div className="p3-heading-actions"><button type="button" className="p3-secondary-button" disabled={!canManage || purgeMutation.isPending} onClick={() => void purgeExpired()}><Archive size={14} />{purgeMutation.isPending ? "Purging…" : "Purge expired"}</button><button type="button" className="p3-primary-button" disabled={!canManage} onClick={openCreate}><Plus size={15} />Create memory</button></div>
      </header>

      <div className="p3-memory-toolbar">
        <label><Search size={14} /><span>Type</span><select value={memoryType} onChange={(event) => setMemoryType(event.target.value as MemoryType | "")}><option value="">All types</option><option value="episodic">Episodic</option><option value="semantic">Semantic</option></select></label>
        <label><span>Scope</span><select value={scope} onChange={(event) => setScope(event.target.value as MemoryScope | "")}><option value="">All scopes</option><option value="user">User</option><option value="agent">Agent</option></select></label>
        <span className="p3-memory-total">{memories.length} active memor{memories.length === 1 ? "y" : "ies"}</span>
      </div>
      {notice && <div className="p3-success-banner" role="status">{notice}</div>}
      {memoriesQuery.isError && <div className="p3-inline-error" role="alert">{getApiErrorMessage(memoriesQuery.error, "Unable to load memories.")}</div>}

      <div className="p3-memory-grid">
        <div className="p3-memory-left-column">
          <MemoryList memories={memories} selectedId={selectedId} loading={memoriesQuery.isLoading} onSelect={(memory) => { setSelectedId(memory.id); setSearchResult(null); }} onRefresh={() => void memoriesQuery.refetch()} />
          <MemorySearch busy={searchMutation.isPending} result={searchResult} error={searchError} onSearch={search} onSelectMemory={(memoryId) => setSelectedId(memoryId)} />
        </div>
        <MemoryDetails memory={detailMemory} loading={Boolean(selectedId) && detailsQuery.isLoading} canManage={canManage} onEdit={openEdit} onDelete={(memory) => void remove(memory)} />
      </div>

      {!canManage && <p className="p3-page-footnote">Your current role can inspect and search memories. Creating, updating, deleting and purging memories requires an administrator or operator role.</p>}
      <p className="p3-page-footnote">Memory records are owner-scoped. Creating, semantic search and content updates use the configured local embedding service; embeddings are never exposed to the frontend.</p>

      {formOpen && <MemoryForm initial={editingMemory} busy={createMutation.isPending || updateMutation.isPending} onClose={() => setFormOpen(false)} onCreate={create} onUpdate={update} />}
    </section>
  );
}
