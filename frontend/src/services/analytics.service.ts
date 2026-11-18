import { api } from "./api";
import type {
  AgentUsageResponse,
  DateRangeParams,
  ObservabilityOverview,
  ProviderUsageResponse,
  TelemetryEventsResponse,
  TelemetryPurgeResponse,
  WorkflowAnalyticsResponse,
} from "../types/observability";

export interface WorkflowListParams extends DateRangeParams {
  limit?: number;
  offset?: number;
}

export interface EventListParams extends DateRangeParams {
  event_type?: string;
  limit?: number;
  offset?: number;
}

export const analyticsService = {
  async getOverview(params: DateRangeParams): Promise<ObservabilityOverview> {
    const response = await api.get<ObservabilityOverview>("/observability/overview", { params });
    return response.data;
  },

  async getProviders(params: DateRangeParams): Promise<ProviderUsageResponse> {
    const response = await api.get<ProviderUsageResponse>("/observability/providers", { params });
    return response.data;
  },

  async getAgents(params: DateRangeParams): Promise<AgentUsageResponse> {
    const response = await api.get<AgentUsageResponse>("/observability/agents", { params });
    return response.data;
  },

  async getWorkflows(params: WorkflowListParams): Promise<WorkflowAnalyticsResponse> {
    const response = await api.get<WorkflowAnalyticsResponse>("/observability/workflows", { params });
    return response.data;
  },

  async getEvents(params: EventListParams): Promise<TelemetryEventsResponse> {
    const response = await api.get<TelemetryEventsResponse>("/observability/events", { params });
    return response.data;
  },

  async purgeTelemetry(): Promise<TelemetryPurgeResponse> {
    const response = await api.post<TelemetryPurgeResponse>("/observability/telemetry/purge");
    return response.data;
  },
};
