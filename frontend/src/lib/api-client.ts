import axios from "axios";

import { readAccessToken } from "../features/auth/token-storage";

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

export const apiClient = axios.create({
  baseURL: configuredBaseUrl || "/api/v1",
  timeout: 30_000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = readAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const requestUrl = error.config?.url ?? "";
      if (!requestUrl.endsWith("/auth/login") && typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("agentops:auth-expired"));
      }
    }
    return Promise.reject(error);
  },
);
