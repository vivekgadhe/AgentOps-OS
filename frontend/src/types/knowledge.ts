export interface KnowledgeDocument {
  id: string;
  filename: string;
  media_type: string;
  sha256: string;
  page_count: number;
  chunk_count: number;
  created_at: string;
}

export interface KnowledgeCitation {
  source_id: string;
  document_id: string;
  filename: string;
  page_number: number | null;
  chunk_index: number;
  content: string;
  similarity: number;
}

export interface KnowledgeSearchRequest {
  query: string;
  top_k?: number;
  document_ids?: string[] | null;
}

export interface KnowledgeSearchResponse {
  query: string;
  results: KnowledgeCitation[];
}

export interface AgentResult {
  agent_name: string;
  status: "succeeded" | "failed";
  summary: string;
  output: Record<string, unknown>;
  error_type: string | null;
  error_message: string | null;
}

export interface KnowledgeAnswerResponse {
  query: string;
  answer: AgentResult;
  citations: KnowledgeCitation[];
}
