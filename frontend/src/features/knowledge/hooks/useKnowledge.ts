import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { knowledgeService } from "../../../services/knowledge.service";
import type { KnowledgeSearchRequest } from "../../../types/knowledge";

export const knowledgeKeys = {
  all: ["knowledge"] as const,
  documents: () => [...knowledgeKeys.all, "documents"] as const,
};

export function useKnowledgeDocuments() {
  return useQuery({
    queryKey: knowledgeKeys.documents(),
    queryFn: knowledgeService.listDocuments,
  });
}

export function useUploadKnowledgeDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: knowledgeService.uploadDocument,
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: knowledgeKeys.all }),
  });
}

export function useDeleteKnowledgeDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: knowledgeService.deleteDocument,
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: knowledgeKeys.all }),
  });
}

export function useKnowledgeSearch() {
  return useMutation({ mutationFn: (payload: KnowledgeSearchRequest) => knowledgeService.search(payload) });
}
