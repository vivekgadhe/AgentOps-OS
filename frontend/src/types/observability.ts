export interface DateRangeParams {
  start_at: string;
  end_at: string;
}

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

export interface ProviderUsageItem {
  provider: string;
  model: string;
  attempt_count: number;
  success_count: number;
  failure_count: number;
  refusal_count: number;
  success_rate: number;
  average_duration_ms: number | null;
}

export interface ProviderUsageResponse extends DateRangeParams {
  items: ProviderUsageItem[];
}

export interface AgentUsageItem {
  agent_name: string;
  generation_attempts: number;
  success_count: number;
  failure_count: number;
  refusal_count: number;
  success_rate: number;
  average_duration_ms: number | null;
}

export interface AgentUsageResponse extends DateRangeParams {
  items: AgentUsageItem[];
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

export interface WorkflowAnalyticsResponse extends DateRangeParams {
  total: number;
  limit: number;
  offset: number;
  items: WorkflowAnalyticsItem[];
}

export interface TelemetryEvent {
  id: string;
  workflow_run_id: string | null;
  request_id: string | null;
  event_type: string;
  component: string;
  agent_name: string | null;
  provider: string;
  model: string;
  outcome: "success" | "failure" | "refused";
  duration_ms: number;
  input_tokens: number | null;
  output_tokens: number | null;
  error_type: string | null;
  attributes: Record<string, unknown>;
  created_at: string;
}

export interface TelemetryEventsResponse extends DateRangeParams {
  total: number;
  limit: number;
  offset: number;
  items: TelemetryEvent[];
}

export interface TelemetryPurgeResponse {
  deleted_count: number;
  retention_days: number;
  cutoff_at: string;
}

export interface WorkflowTrendPoint {
  date: string;
  succeeded: number;
  failed: number;
  cancelled: number;
  active: number;
}
