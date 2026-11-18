import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), delete: vi.fn() }));

vi.mock("../lib/api-client", () => ({
  apiClient: { get: mocks.get, post: mocks.post, delete: mocks.delete },
}));

import { knowledgeService } from "./knowledge.service";

describe("knowledgeService", () => {
  beforeEach(() => vi.clearAllMocks());

  it("lists the authenticated user's documents", async () => {
    mocks.get.mockResolvedValue({ data: [] });
    await expect(knowledgeService.listDocuments()).resolves.toEqual([]);
    expect(mocks.get).toHaveBeenCalledWith("/knowledge/documents");
  });

  it("uploads a document as multipart form data", async () => {
    const file = new File(["phase three"], "notes.txt", { type: "text/plain" });
    const document = { id: "doc-1", filename: "notes.txt" };
    mocks.post.mockResolvedValue({ data: document });
    await expect(knowledgeService.uploadDocument(file)).resolves.toEqual(document);
    expect(mocks.post).toHaveBeenCalledWith("/knowledge/documents", expect.any(FormData));
    expect((mocks.post.mock.calls[0]?.[1] as FormData).get("file")).toBe(file);
  });

  it("searches with the supplied query and top-k contract", async () => {
    const payload = { query: "retention policy", top_k: 5 };
    mocks.post.mockResolvedValue({ data: { query: payload.query, results: [] } });
    await knowledgeService.search(payload);
    expect(mocks.post).toHaveBeenCalledWith("/knowledge/search", payload);
  });

  it("deletes a document by its identifier", async () => {
    mocks.delete.mockResolvedValue({ data: null });
    await knowledgeService.deleteDocument("doc-1");
    expect(mocks.delete).toHaveBeenCalledWith("/knowledge/documents/doc-1");
  });
});
