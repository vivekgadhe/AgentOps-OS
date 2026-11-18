import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() }));

vi.mock("../lib/api-client", () => ({
  apiClient: { get: mocks.get, post: mocks.post, patch: mocks.patch, delete: mocks.delete },
}));

import { memoryService } from "./memory.service";

describe("memoryService", () => {
  beforeEach(() => vi.clearAllMocks());

  it("lists memories with optional owner-scoped filters", async () => {
    mocks.get.mockResolvedValue({ data: [] });
    const params = { memory_type: "semantic" as const, memory_scope: "user" as const, limit: 25 };
    await expect(memoryService.list(params)).resolves.toEqual([]);
    expect(mocks.get).toHaveBeenCalledWith("/memories", { params });
  });

  it("creates a memory through the authenticated memory API", async () => {
    const payload = { memory_type: "semantic" as const, memory_scope: "user" as const, content: "Prefers concise reports", importance: 0.7, metadata_json: {} };
    const memory = { id: "memory-1", ...payload };
    mocks.post.mockResolvedValue({ data: memory });
    await expect(memoryService.create(payload)).resolves.toEqual(memory);
    expect(mocks.post).toHaveBeenCalledWith("/memories", payload);
  });

  it("performs semantic memory search", async () => {
    const payload = { query: "report preferences", top_k: 5 };
    mocks.post.mockResolvedValue({ data: { query: payload.query, results: [] } });
    await memoryService.search(payload);
    expect(mocks.post).toHaveBeenCalledWith("/memories/search", payload);
  });

  it("updates, retrieves and deletes a memory using its id", async () => {
    const memory = { id: "memory-1", content: "Updated" };
    mocks.get.mockResolvedValue({ data: memory });
    mocks.patch.mockResolvedValue({ data: memory });
    mocks.delete.mockResolvedValue({ data: null });
    await expect(memoryService.get("memory-1")).resolves.toEqual(memory);
    await expect(memoryService.update("memory-1", { importance: 0.9 })).resolves.toEqual(memory);
    await memoryService.delete("memory-1");
    expect(mocks.get).toHaveBeenCalledWith("/memories/memory-1");
    expect(mocks.patch).toHaveBeenCalledWith("/memories/memory-1", { importance: 0.9 });
    expect(mocks.delete).toHaveBeenCalledWith("/memories/memory-1");
  });

  it("purges only expired memories for the current authenticated user", async () => {
    mocks.delete.mockResolvedValue({ data: { deleted_count: 2 } });
    await expect(memoryService.purgeExpired()).resolves.toEqual({ deleted_count: 2 });
    expect(mocks.delete).toHaveBeenCalledWith("/memories/expired");
  });
});
