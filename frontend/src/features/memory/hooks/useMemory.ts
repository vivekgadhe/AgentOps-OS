import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { memoryService, type MemoryListParams } from "../../../services/memory.service";
import type { MemoryCreateRequest, MemorySearchRequest, MemoryUpdateRequest } from "../../../types/memory";

export const memoryKeys = {
  all: ["memories"] as const,
  lists: () => [...memoryKeys.all, "list"] as const,
  list: (params: MemoryListParams) => [...memoryKeys.lists(), params] as const,
  detail: (id: string) => [...memoryKeys.all, "detail", id] as const,
};

export function useMemories(params: MemoryListParams = {}) {
  return useQuery({ queryKey: memoryKeys.list(params), queryFn: () => memoryService.list(params) });
}

export function useMemoryDetails(memoryId: string | null) {
  return useQuery({
    queryKey: memoryKeys.detail(memoryId ?? ""),
    queryFn: () => memoryService.get(memoryId as string),
    enabled: Boolean(memoryId),
  });
}

function useInvalidateMemories() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: memoryKeys.all });
}

export function useCreateMemory() {
  const invalidate = useInvalidateMemories();
  return useMutation({ mutationFn: (payload: MemoryCreateRequest) => memoryService.create(payload), onSuccess: invalidate });
}

export function useUpdateMemory() {
  const invalidate = useInvalidateMemories();
  return useMutation({ mutationFn: ({ id, payload }: { id: string; payload: MemoryUpdateRequest }) => memoryService.update(id, payload), onSuccess: invalidate });
}

export function useDeleteMemory() {
  const invalidate = useInvalidateMemories();
  return useMutation({ mutationFn: memoryService.delete, onSuccess: invalidate });
}

export function useSearchMemories() {
  return useMutation({ mutationFn: (payload: MemorySearchRequest) => memoryService.search(payload) });
}

export function usePurgeExpiredMemories() {
  const invalidate = useInvalidateMemories();
  return useMutation({ mutationFn: memoryService.purgeExpired, onSuccess: invalidate });
}
