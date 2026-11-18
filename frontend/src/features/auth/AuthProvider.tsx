import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getApiErrorMessage } from "../../lib/api-error";
import { authApi } from "./auth.api";
import type { AuthUser, LoginCredentials, RegistrationPayload } from "./auth.types";
import {
  clearAccessToken,
  readAccessToken,
  saveAccessToken,
  setRememberedEmail,
  type TokenPersistence,
} from "./token-storage";

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials, rememberMe: boolean) => Promise<void>;
  register: (payload: RegistrationPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    clearAccessToken();
    setUser(null);
  }, []);

  useEffect(() => {
    let active = true;

    const handleExpired = () => {
      if (active) logout();
    };

    window.addEventListener("agentops:auth-expired", handleExpired);

    async function restoreSession() {
      if (!readAccessToken()) {
        if (active) setIsLoading(false);
        return;
      }

      try {
        const currentUser = await authApi.me();
        if (active) setUser(currentUser);
      } catch {
        clearAccessToken();
        if (active) setUser(null);
      } finally {
        if (active) setIsLoading(false);
      }
    }

    void restoreSession();

    return () => {
      active = false;
      window.removeEventListener("agentops:auth-expired", handleExpired);
    };
  }, [logout]);

  const login = useCallback(
    async (credentials: LoginCredentials, rememberMe: boolean) => {
      const tokenResponse = await authApi.login(credentials);
      const persistence: TokenPersistence = rememberMe ? "persistent" : "session";
      saveAccessToken(tokenResponse.access_token, persistence);
      setRememberedEmail(credentials.email, rememberMe);

      try {
        const currentUser = await authApi.me();
        setUser(currentUser);
      } catch (error) {
        clearAccessToken();
        throw new Error(getApiErrorMessage(error, "Unable to load your account."));
      }
    },
    [],
  );

  const register = useCallback(async (payload: RegistrationPayload) => {
    const tokenResponse = await authApi.register(payload);
    saveAccessToken(tokenResponse.access_token, "session");

    try {
      const currentUser = await authApi.me();
      setUser(currentUser);
    } catch (error) {
      clearAccessToken();
      throw new Error(
        getApiErrorMessage(error, "Registration succeeded, but the new session could not be loaded."),
      );
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider.");
  return context;
}
