import { api } from "./api";
import type {
  AgentMemory,
  MemoryCreateRequest,
  MemoryPurgeResponse,
  MemorySearchRequest,
  MemorySearchResponse,
  MemoryUpdateRequest,
  MemoryType,
  MemoryScope,
} from "../types/memory";

export interface MemoryListParams {
  memory_type?: MemoryType;
  memory_scope?: MemoryScope;
  agent_key?: string;
  limit?: number;
}

export const memoryService = {
  async list(params: MemoryListParams = {}): Promise<AgentMemory[]> {
    const response = await api.get<AgentMemory[]>("/memories", { params });
    return response.data;
  },

  async get(memoryId: string): Promise<AgentMemory> {
    const response = await api.get<AgentMemory>(`/memories/${memoryId}`);
    return response.data;
  },

  async create(payload: MemoryCreateRequest): Promise<AgentMemory> {
    const response = await api.post<AgentMemory>("/memories", payload);
    return response.data;
  },

  async update(memoryId: string, payload: MemoryUpdateRequest): Promise<AgentMemory> {
    const response = await api.patch<AgentMemory>(`/memories/${memoryId}`, payload);
    return response.data;
  },

  async delete(memoryId: string): Promise<void> {
    await api.delete(`/memories/${memoryId}`);
  },

  async search(payload: MemorySearchRequest): Promise<MemorySearchResponse> {
    const response = await api.post<MemorySearchResponse>("/memories/search", payload);
    return response.data;
  },

  async purgeExpired(): Promise<MemoryPurgeResponse> {
    const response = await api.delete<MemoryPurgeResponse>("/memories/expired");
    return response.data;
  },
};
