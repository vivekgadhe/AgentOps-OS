import { api } from "./api";
import type {
  KnowledgeAnswerResponse,
  KnowledgeSearchRequest,
} from "../types/knowledge";

/**
 * Local LLM generation can take longer than ordinary API requests,
 * especially when Ollama is loading a model for the first time.
 */
const AGENT_REQUEST_TIMEOUT_MS = 240_000;

export const agentService = {
  async askAnalysisAgent(
    payload: KnowledgeSearchRequest,
  ): Promise<KnowledgeAnswerResponse> {
    const response = await api.post<KnowledgeAnswerResponse>(
      "/knowledge/query",
      payload,
      {
        timeout: AGENT_REQUEST_TIMEOUT_MS,
      },
    );

    return response.data;
  },

  async askReportAgent(
    payload: KnowledgeSearchRequest,
  ): Promise<KnowledgeAnswerResponse> {
    const response = await api.post<KnowledgeAnswerResponse>(
      "/knowledge/report",
      payload,
      {
        timeout: AGENT_REQUEST_TIMEOUT_MS,
      },
    );

    return response.data;
  },
};