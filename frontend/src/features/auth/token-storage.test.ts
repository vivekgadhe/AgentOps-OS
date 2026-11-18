import { afterEach, describe, expect, it, vi } from "vitest";

import {
  clearAccessToken,
  getRememberedEmail,
  readAccessToken,
  saveAccessToken,
  setRememberedEmail,
} from "./token-storage";

function createMemoryStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear() {
      values.clear();
    },
    getItem(key: string) {
      return values.get(key) ?? null;
    },
    key(index: number) {
      return [...values.keys()][index] ?? null;
    },
    removeItem(key: string) {
      values.delete(key);
    },
    setItem(key: string, value: string) {
      values.set(key, String(value));
    },
  };
}

const localStorageMock = createMemoryStorage();
const sessionStorageMock = createMemoryStorage();

function installWindowMock() {
  vi.stubGlobal("window", {
    localStorage: localStorageMock,
    sessionStorage: sessionStorageMock,
  });
}

describe("token storage", () => {
  afterEach(() => {
    localStorageMock.clear();
    sessionStorageMock.clear();
    vi.unstubAllGlobals();
  });

  it("stores a remembered token in local storage", () => {
    installWindowMock();
    saveAccessToken("persistent-token", "persistent");

    expect(localStorageMock.getItem("agentops.access_token")).toBe("persistent-token");
    expect(sessionStorageMock.getItem("agentops.access_token")).toBeNull();
    expect(readAccessToken()).toBe("persistent-token");
  });

  it("stores a non-remembered token in session storage", () => {
    installWindowMock();
    saveAccessToken("session-token", "session");

    expect(sessionStorageMock.getItem("agentops.access_token")).toBe("session-token");
    expect(localStorageMock.getItem("agentops.access_token")).toBeNull();
    expect(readAccessToken()).toBe("session-token");
  });

  it("removes both token copies on logout", () => {
    installWindowMock();
    localStorageMock.setItem("agentops.access_token", "persistent-token");
    sessionStorageMock.setItem("agentops.access_token", "session-token");

    clearAccessToken();

    expect(readAccessToken()).toBeNull();
  });

  it("remembers an email only when remember me is enabled", () => {
    installWindowMock();
    setRememberedEmail("  ADMIN@EXAMPLE.COM  ", true);
    expect(getRememberedEmail()).toBe("admin@example.com");

    setRememberedEmail("admin@example.com", false);
    expect(getRememberedEmail()).toBe("");
  });
});
