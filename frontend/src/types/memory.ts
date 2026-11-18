export type MemoryType = "episodic" | "semantic";
export type MemoryScope = "user" | "agent";
export type MemorySourceType = "user" | "agent" | "workflow";

export interface AgentMemory {
  id: string;
  owner_user_id: string;
  memory_type: MemoryType;
  memory_scope: MemoryScope;
  agent_key: string | null;
  content: string;
  embedding_model: string;
  confidence: number;
  importance: number;
  source_type: MemorySourceType;
  source_workflow_run_id: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  last_accessed_at: string;
  expires_at: string | null;
}

export interface MemoryCreateRequest {
  memory_type: MemoryType;
  memory_scope: MemoryScope;
  agent_key?: string | null;
  content: string;
  importance: number;
  ttl_days?: number | null;
  metadata_json: Record<string, unknown>;
}

export interface MemoryUpdateRequest {
  content?: string;
  importance?: number;
  ttl_days?: number | null;
}

export interface MemorySearchRequest {
  query: string;
  agent_key?: string | null;
  memory_type?: MemoryType | null;
  top_k?: number;
  min_similarity?: number;
}

export interface MemorySearchHit {
  memory: AgentMemory;
  similarity: number;
  relevance_score: number;
}

export interface MemorySearchResponse {
  query: string;
  results: MemorySearchHit[];
}

export interface MemoryPurgeResponse {
  deleted_count: number;
}
