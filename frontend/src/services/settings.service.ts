import { api } from "./api";
import { authApi } from "../features/auth/auth.api";
import type { InvitationCreatePayload, InvitationCreateResponse } from "../features/auth/auth.types";

export type AIProviderName = "ollama" | "openai" | "groq";

export interface AIProviderConfig {
  id: string;
  provider: AIProviderName;
  model_name: string;
  api_key_configured: boolean;
  base_url: string | null;
  priority: number;
  enabled: boolean;
}

export interface AIProviderUpsertPayload {
  model_name: string;
  api_key?: string;
  base_url?: string | null;
  priority: number;
  enabled: boolean;
}

export interface AIProviderTestResult {
  provider: AIProviderName;
  model_name: string;
  success: boolean;
  message: string;
}

export interface BackendReadiness {
  status: "ok" | "unavailable";
  db: "up" | "down";
}

export const settingsService = {
  async getProviders(): Promise<AIProviderConfig[]> {
    const response = await api.get<AIProviderConfig[]>("/ai-providers");
    return response.data;
  },

  async saveProvider(provider: AIProviderName, payload: AIProviderUpsertPayload): Promise<AIProviderConfig> {
    const response = await api.put<AIProviderConfig>(`/ai-providers/${provider}`, payload);
    return response.data;
  },

  async deleteProvider(provider: AIProviderName): Promise<void> {
    await api.delete(`/ai-providers/${provider}`);
  },

  async testProviderChain(): Promise<AIProviderTestResult> {
    const response = await api.post<AIProviderTestResult>("/ai-providers/test");
    return response.data;
  },

  async getReadiness(): Promise<BackendReadiness> {
    const response = await api.get<BackendReadiness>("/health/ready");
    return response.data;
  },

  createInvitation(payload: InvitationCreatePayload): Promise<InvitationCreateResponse> {
    return authApi.createInvitation(payload);
  },
};
