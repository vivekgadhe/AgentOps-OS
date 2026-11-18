const ACCESS_TOKEN_KEY = "agentops.access_token";
const REMEMBERED_EMAIL_KEY = "agentops.remembered_email";

export type TokenPersistence = "session" | "persistent";

export function readAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    window.localStorage.getItem(ACCESS_TOKEN_KEY) ??
    window.sessionStorage.getItem(ACCESS_TOKEN_KEY)
  );
}

export function saveAccessToken(token: string, persistence: TokenPersistence): void {
  if (typeof window === "undefined") return;

  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.sessionStorage.removeItem(ACCESS_TOKEN_KEY);

  const storage = persistence === "persistent" ? window.localStorage : window.sessionStorage;
  storage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.sessionStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function getRememberedEmail(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(REMEMBERED_EMAIL_KEY) ?? "";
}

export function setRememberedEmail(email: string, remember: boolean): void {
  if (typeof window === "undefined") return;
  if (remember && email.trim()) {
    window.localStorage.setItem(REMEMBERED_EMAIL_KEY, email.trim().toLowerCase());
  } else {
    window.localStorage.removeItem(REMEMBERED_EMAIL_KEY);
  }
}
