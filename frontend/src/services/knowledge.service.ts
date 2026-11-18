import { api } from "./api";
import type {
  KnowledgeDocument,
  KnowledgeSearchRequest,
  KnowledgeSearchResponse,
} from "../types/knowledge";

export const knowledgeService = {
  async listDocuments(): Promise<KnowledgeDocument[]> {
    const response = await api.get<KnowledgeDocument[]>("/knowledge/documents");
    return response.data;
  },

  async uploadDocument(file: File): Promise<KnowledgeDocument> {
    const form = new FormData();
    form.append("file", file);
    const response = await api.post<KnowledgeDocument>("/knowledge/documents", form);
    return response.data;
  },

  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/knowledge/documents/${documentId}`);
  },

  async search(payload: KnowledgeSearchRequest): Promise<KnowledgeSearchResponse> {
    const response = await api.post<KnowledgeSearchResponse>("/knowledge/search", payload);
    return response.data;
  },
};

export type { KnowledgeAnswerResponse } from "../types/knowledge";
