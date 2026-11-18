import { apiClient } from "../../lib/api-client";
import type {
  AuthUser,
  InvitationCreatePayload,
  InvitationCreateResponse,
  LoginCredentials,
  MessageResponse,
  PasswordResetPayload,
  PasswordResetStartPayload,
  RegistrationOtpRequestPayload,
  RegistrationPayload,
  TokenResponse,
} from "./auth.types";

export const authApi = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>("/auth/login", credentials);
    return response.data;
  },

  async requestRegistrationOtp(
    payload: RegistrationOtpRequestPayload,
  ): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>(
      "/auth/register/request",
      payload,
    );
    return response.data;
  },

  async register(payload: RegistrationPayload): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>("/auth/register", payload);
    return response.data;
  },

  // Optional administrator-controlled invitations remain supported by the API.
  async createInvitation(
    payload: InvitationCreatePayload,
  ): Promise<InvitationCreateResponse> {
    const response = await apiClient.post<InvitationCreateResponse>(
      "/auth/invitations",
      payload,
    );
    return response.data;
  },

  async requestPasswordReset(
    payload: PasswordResetStartPayload,
  ): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>(
      "/auth/password-reset/request",
      payload,
    );
    return response.data;
  },

  async resetPassword(payload: PasswordResetPayload): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>(
      "/auth/password-reset",
      payload,
    );
    return response.data;
  },

  async me(): Promise<AuthUser> {
    const response = await apiClient.get<AuthUser>("/auth/me");
    return response.data;
  },
};
