import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ post: vi.fn() }));

vi.mock("../lib/api-client", () => ({ apiClient: { post: mocks.post } }));

import { agentService } from "./agent.service";

describe("agentService", () => {
  beforeEach(() => vi.clearAllMocks());

  it("routes Analysis Agent requests to the knowledge query endpoint", async () => {
    const payload = { query: "Summarize the policy", top_k: 5 };
    const result = { query: payload.query, answer: { agent_name: "analysis_agent" }, citations: [] };
    mocks.post.mockResolvedValue({ data: result });
    await expect(agentService.askAnalysisAgent(payload)).resolves.toEqual(result);
    expect(mocks.post).toHaveBeenCalledWith("/knowledge/query", payload, {
      timeout: 240_000,
    });
  });

  it("routes Report Agent requests to the knowledge report endpoint", async () => {
    const payload = { query: "Prepare a summary report", top_k: 5 };
    const result = { query: payload.query, answer: { agent_name: "report_agent" }, citations: [] };
    mocks.post.mockResolvedValue({ data: result });
    await expect(agentService.askReportAgent(payload)).resolves.toEqual(result);
    expect(mocks.post).toHaveBeenCalledWith("/knowledge/report", payload, {
      timeout: 240_000,
    });
  });
});
