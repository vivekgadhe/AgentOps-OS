import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock("../lib/api-client", () => ({ apiClient: { get: mocks.get, post: mocks.post } }));

import { analyticsService } from "./analytics.service";

const range = { start_at: "2026-11-01T00:00:00.000Z", end_at: "2026-11-16T00:00:00.000Z" };

describe("analyticsService", () => {
  beforeEach(() => vi.clearAllMocks());

  it("loads the owner-scoped observability overview with its date range", async () => {
    const data = { workflow_count: 3, workflow_status_counts: { succeeded: 2 } };
    mocks.get.mockResolvedValue({ data });
    await expect(analyticsService.getOverview(range)).resolves.toEqual(data);
    expect(mocks.get).toHaveBeenCalledWith("/observability/overview", { params: range });
  });

  it("loads provider, agent and workflow analytics using actual API routes", async () => {
    mocks.get.mockResolvedValue({ data: { items: [] } });
    await analyticsService.getProviders(range);
    await analyticsService.getAgents(range);
    await analyticsService.getWorkflows({ ...range, limit: 100, offset: 0 });
    expect(mocks.get).toHaveBeenNthCalledWith(1, "/observability/providers", { params: range });
    expect(mocks.get).toHaveBeenNthCalledWith(2, "/observability/agents", { params: range });
    expect(mocks.get).toHaveBeenNthCalledWith(3, "/observability/workflows", { params: { ...range, limit: 100, offset: 0 } });
  });

  it("filters telemetry events and supports safe telemetry retention purge", async () => {
    mocks.get.mockResolvedValue({ data: { items: [], total: 0 } });
    mocks.post.mockResolvedValue({ data: { deleted_count: 0, retention_days: 90, cutoff_at: "2026-08-18T00:00:00Z" } });
    await analyticsService.getEvents({ ...range, event_type: "llm_attempt", limit: 25, offset: 0 });
    await analyticsService.purgeTelemetry();
    expect(mocks.get).toHaveBeenCalledWith("/observability/events", { params: { ...range, event_type: "llm_attempt", limit: 25, offset: 0 } });
    expect(mocks.post).toHaveBeenCalledWith("/observability/telemetry/purge");
  });
});
