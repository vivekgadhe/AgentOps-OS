export type UserRole = "admin" | "operator" | "viewer";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer" | string;
}

export interface AuthUser {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface RegistrationOtpRequestPayload {
  email: string;
}

export interface RegistrationPayload {
  email: string;
  otp: string;
  password: string;
}

export interface PasswordResetPayload {
  email: string;
  token: string;
  new_password: string;
}

export interface PasswordResetStartPayload {
  email: string;
}

export interface MessageResponse {
  message: string;
}

// Retained for the optional administrator-managed invitation screen.
export interface InvitationCreatePayload {
  email: string;
  role: UserRole;
}

export interface InvitationCreateResponse {
  message: string;
  email: string;
  expires_at: string;
}
