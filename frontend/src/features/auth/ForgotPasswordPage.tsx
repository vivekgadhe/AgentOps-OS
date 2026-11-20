import { useState, type FormEvent } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  KeyRound,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../../components/ui/Button";
import { TextInput } from "../../components/ui/TextInput";
import { AuthLayout } from "../../layouts/AuthLayout";
import { getApiErrorMessage } from "../../lib/api-error";
import { authApi } from "./auth.api";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [codeRequested, setCodeRequested] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function requestCode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const response = await authApi.requestPasswordReset({
        email: email.trim().toLowerCase(),
      });

      setCodeRequested(true);
      setSuccessMessage(response.message);
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(
          error,
          "Unable to request a reset code. Please try again later.",
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function resetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (password !== confirmPassword) {
      setErrorMessage("The passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await authApi.resetPassword({
        email: email.trim().toLowerCase(),
        token: otp.trim(),
        new_password: password,
      });

      setSuccessMessage(response.message);
      setOtp("");
      setPassword("");
      setConfirmPassword("");
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(
          error,
          "Password reset failed. Check the code and try again.",
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function resendCode() {
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const response = await authApi.requestPasswordReset({
        email: email.trim().toLowerCase(),
      });

      setSuccessMessage(response.message);
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, "Unable to resend the code."),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout>
      <section className="auth-brand" aria-label="AgentOps-OS">
        <img
          src="/docs/logos/logo.png"
          alt="AgentOps-OS"
          className="auth-brand-logo"
        />
        <p>
          Build, run and monitor AI agents
          <br />
          for real business workflows
        </p>
      </section>

      <section className="login-card" aria-labelledby="reset-title">
        <div className="login-card-topline">
          <span className="login-badge">
            <ShieldCheck size={14} /> ACCOUNT RECOVERY
          </span>
          <span className="login-lock">
            <KeyRound size={15} />
          </span>
        </div>

        <div className="login-heading">
          <h2 id="reset-title">Reset your password</h2>
          <p>
            We will email you a six-digit, single-use verification code.
          </p>
        </div>

        <form
          onSubmit={codeRequested ? resetPassword : requestCode}
          className="login-form"
        >
          <div className="form-field">
            <label htmlFor="reset-email">Email address</label>
            <div className="input-wrap">
              <Mail
                className="input-leading-icon"
                size={17}
                aria-hidden="true"
              />
              <TextInput
                id="reset-email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                maxLength={320}
                disabled={isSubmitting || codeRequested}
              />
            </div>
          </div>

          {codeRequested && (
            <>
              <div className="form-field">
                <label htmlFor="reset-otp">
                  Six-digit verification code
                </label>
                <div className="input-wrap">
                  <KeyRound
                    className="input-leading-icon"
                    size={17}
                    aria-hidden="true"
                  />
                  <TextInput
                    id="reset-otp"
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    placeholder="Enter the code from your email"
                    value={otp}
                    onChange={(event) =>
                      setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
                    }
                    required
                    minLength={6}
                    maxLength={6}
                    pattern="[0-9]{6}"
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="new-password">New password</label>
                <div className="input-wrap">
                  <LockKeyhole
                    className="input-leading-icon"
                    size={17}
                    aria-hidden="true"
                  />
                  <TextInput
                    id="new-password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="At least 12 characters"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    minLength={12}
                    maxLength={128}
                    className="password-input"
                    disabled={isSubmitting}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff size={17} />
                    ) : (
                      <Eye size={17} />
                    )}
                  </button>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="confirm-new-password">
                  Confirm new password
                </label>
                <div className="input-wrap">
                  <LockKeyhole
                    className="input-leading-icon"
                    size={17}
                    aria-hidden="true"
                  />
                  <TextInput
                    id="confirm-new-password"
                    type={showConfirmPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="Enter your new password again"
                    value={confirmPassword}
                    onChange={(event) =>
                      setConfirmPassword(event.target.value)
                    }
                    required
                    minLength={12}
                    maxLength={128}
                    className="password-input"
                    disabled={isSubmitting}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowConfirmPassword((value) => !value)
                    }
                    aria-label={
                      showConfirmPassword
                        ? "Hide confirm password"
                        : "Show confirm password"
                    }
                  >
                    {showConfirmPassword ? (
                      <EyeOff size={17} />
                    ) : (
                      <Eye size={17} />
                    )}
                  </button>
                </div>
              </div>
            </>
          )}

          {errorMessage && (
            <div className="form-alert" role="alert">
              <span className="alert-dot" />
              {errorMessage}
            </div>
          )}

          {successMessage && (
            <div className="auth-success" role="status">
              {successMessage}{" "}
              {codeRequested && !otp && "Check your inbox and spam folder."}{" "}
              {successMessage.startsWith("Password updated") && (
                <Link to="/login">Sign in</Link>
              )}
            </div>
          )}

          {!codeRequested ? (
            <Button
              type="submit"
              size="lg"
              className="login-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="button-spinner" /> Sending code…
                </>
              ) : (
                <>
                  Send verification code <ArrowRight size={17} />
                </>
              )}
            </Button>
          ) : (
            <>
              <Button
                type="submit"
                size="lg"
                className="login-submit"
                disabled={
                  isSubmitting ||
                  Boolean(successMessage?.startsWith("Password updated"))
                }
              >
                {isSubmitting ? (
                  <>
                    <span className="button-spinner" /> Updating password…
                  </>
                ) : (
                  <>
                    Update password <ArrowRight size={17} />
                  </>
                )}
              </Button>

              <button
                type="button"
                className="text-action"
                disabled={isSubmitting}
                onClick={resendCode}
              >
                Resend code
              </button>
            </>
          )}
        </form>

        <div className="login-divider">
          <span /> <span>SECURE ACCESS</span> <span />
        </div>

        <Link className="auth-back-link" to="/login">
          <ArrowLeft size={14} /> Back to sign in
        </Link>
      </section>

      <div className="auth-trust-note">
        <span>
          <ShieldCheck size={14} /> Protected workspace
        </span>
        <span className="trust-separator">•</span>
        <span>AI operations, under control</span>
      </div>
    </AuthLayout>
  );
}