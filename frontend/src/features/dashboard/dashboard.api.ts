import { apiClient } from "../../lib/api-client";
import type {
  ApprovalDecisionResponse,
  ApprovalItem,
  KnowledgeDocument,
  ObservabilityOverview,
  WorkflowAnalyticsResponse,
  WorkflowResponse,
  WorkflowTaskCreate,
} from "./dashboard.types";

export function reportingWindow(days: number): { start_at: string; end_at: string } {
  const end = new Date();
  const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000);
  return { start_at: start.toISOString(), end_at: end.toISOString() };
}

export const dashboardApi = {
  async overview(days = 30): Promise<ObservabilityOverview> {
    const response = await apiClient.get<ObservabilityOverview>("/observability/overview", {
      params: reportingWindow(days),
    });
    return response.data;
  },
  async workflows(days = 30, limit = 100): Promise<WorkflowAnalyticsResponse> {
    const response = await apiClient.get<WorkflowAnalyticsResponse>("/observability/workflows", {
      params: { ...reportingWindow(days), limit, offset: 0 },
    });
    return response.data;
  },
  async approvals(): Promise<ApprovalItem[]> {
    const response = await apiClient.get<ApprovalItem[]>("/approvals");
    return response.data;
  },
  async documents(): Promise<KnowledgeDocument[]> {
    const response = await apiClient.get<KnowledgeDocument[]>("/knowledge/documents");
    return response.data;
  },
};

export const workflowApi = {
  async create(payload: { goal: string; tasks: WorkflowTaskCreate[] }): Promise<WorkflowResponse> {
    const response = await apiClient.post<WorkflowResponse>("/runs", payload);
    return response.data;
  },
  async get(runId: string): Promise<WorkflowResponse> {
    const response = await apiClient.get<WorkflowResponse>(`/runs/${runId}`);
    return response.data;
  },
  async execute(runId: string): Promise<WorkflowResponse> {
    const response = await apiClient.post<WorkflowResponse>(`/runs/${runId}/execute`);
    return response.data;
  },
};

export const approvalsApi = {
  async list(): Promise<ApprovalItem[]> {
    const response = await apiClient.get<ApprovalItem[]>("/approvals");
    return response.data;
  },
  async get(approvalId: string): Promise<ApprovalItem> {
    const response = await apiClient.get<ApprovalItem>(`/approvals/${approvalId}`);
    return response.data;
  },
  async approve(approvalId: string, reason: string): Promise<ApprovalDecisionResponse> {
    const response = await apiClient.post<ApprovalDecisionResponse>(
      `/approvals/${approvalId}/approve`,
      { reason: reason.trim() || null },
    );
    return response.data;
  },
  async reject(approvalId: string, reason: string): Promise<ApprovalDecisionResponse> {
    const response = await apiClient.post<ApprovalDecisionResponse>(
      `/approvals/${approvalId}/reject`,
      { reason: reason.trim() || null },
    );
    return response.data;
  },
  async cancel(approvalId: string): Promise<ApprovalDecisionResponse> {
    const response = await apiClient.post<ApprovalDecisionResponse>(`/approvals/${approvalId}/cancel`);
    return response.data;
  },
};
