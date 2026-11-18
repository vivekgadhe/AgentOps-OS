export interface ObservabilityOverview {
  start_at: string;
  end_at: string;
  workflow_count: number;
  workflow_status_counts: Record<string, number>;
  workflow_success_rate: number;
  average_workflow_duration_ms: number | null;
  task_count: number;
  task_status_counts: Record<string, number>;
  task_success_rate: number;
  average_task_duration_ms: number | null;
  llm_attempt_count: number;
  llm_success_count: number;
  llm_failure_count: number;
  llm_refusal_count: number;
  llm_success_rate: number;
  average_llm_duration_ms: number | null;
}

export interface WorkflowAnalyticsItem {
  id: string;
  goal: string;
  status: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  task_count: number;
  succeeded_task_count: number;
  failed_task_count: number;
}

export interface WorkflowAnalyticsResponse {
  start_at: string;
  end_at: string;
  total: number;
  limit: number;
  offset: number;
  items: WorkflowAnalyticsItem[];
}

export interface WorkflowTaskCreate {
  key: string;
  name: string;
  tool_name: string;
  input_data: Record<string, unknown>;
  max_attempts: number;
  timeout_seconds: number;
  depends_on: string[];
}

export interface WorkflowTask {
  id: string;
  key: string;
  name: string;
  tool_name: string | null;
  status: string;
  input_data: Record<string, unknown> | null;
  output_data: Record<string, unknown> | null;
  error: Record<string, unknown> | null;
  attempt_count: number;
  max_attempts: number;
  started_at: string | null;
  finished_at: string | null;
  depends_on: string[];
}

export interface WorkflowResponse {
  id: string;
  goal: string;
  status: string;
  plan: Record<string, unknown> | null;
  error: Record<string, unknown> | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
  tasks: WorkflowTask[];
}

export interface ApprovalItem {
  id: string;
  workflow_run_id: string;
  task_run_id: string;
  requester_user_id: string;
  decided_by_user_id: string | null;
  tool_name: string;
  action_summary: string;
  input_snapshot: Record<string, unknown>;
  status: 'pending' | 'approved' | 'rejected' | 'expired' | 'cancelled' | 'executed';
  decision_reason: string | null;
  requested_at: string;
  expires_at: string;
  decided_at: string | null;
}

export interface ApprovalDecisionResponse {
  approval: ApprovalItem;
  workflow_status: string;
}

export interface KnowledgeDocument {
  id: string;
  filename: string;
  media_type: string;
  sha256: string;
  page_count: number;
  chunk_count: number;
  created_at: string;
}
