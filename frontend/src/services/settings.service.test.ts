import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ get: vi.fn(), put: vi.fn(), post: vi.fn(), delete: vi.fn() }));
vi.mock("../lib/api-client", () => ({ apiClient: mocks }));

import { settingsService } from "./settings.service";

describe("settingsService", () => {
  beforeEach(() => vi.clearAllMocks());

  it("loads account-scoped provider configuration without credentials", async () => {
    const providers = [{ provider: "ollama", model_name: "qwen3.5:0.8b", api_key_configured: false }];
    mocks.get.mockResolvedValue({ data: providers });
    await expect(settingsService.getProviders()).resolves.toEqual(providers);
    expect(mocks.get).toHaveBeenCalledWith("/ai-providers");
  });

  it("saves and deletes provider configuration through supported routes", async () => {
    const payload = { model_name: "qwen3.5:0.8b", base_url: "http://localhost:11434", priority: 0, enabled: true };
    const provider = { provider: "ollama", ...payload, api_key_configured: false };
    mocks.put.mockResolvedValue({ data: provider });
    mocks.delete.mockResolvedValue({ data: null });
    await expect(settingsService.saveProvider("ollama", payload)).resolves.toEqual(provider);
    await settingsService.deleteProvider("ollama");
    expect(mocks.put).toHaveBeenCalledWith("/ai-providers/ollama", payload);
    expect(mocks.delete).toHaveBeenCalledWith("/ai-providers/ollama");
  });

  it("tests the configured provider fallback chain and checks backend readiness", async () => {
    const tested = { provider: "ollama", model_name: "qwen3.5:0.8b", success: true, message: "ok" };
    mocks.post.mockResolvedValue({ data: tested });
    mocks.get.mockResolvedValue({ data: { status: "ok", db: "up" } });
    await expect(settingsService.testProviderChain()).resolves.toEqual(tested);
    await expect(settingsService.getReadiness()).resolves.toEqual({ status: "ok", db: "up" });
    expect(mocks.post).toHaveBeenCalledWith("/ai-providers/test");
    expect(mocks.get).toHaveBeenCalledWith("/health/ready");
  });
});
