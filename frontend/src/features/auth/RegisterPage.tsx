import { useEffect, useState, type FormEvent } from "react";
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
import { Link, useNavigate } from "react-router-dom";

import { Button } from "../../components/ui/Button";
import { TextInput } from "../../components/ui/TextInput";
import { AuthLayout } from "../../layouts/AuthLayout";
import { getApiErrorMessage } from "../../lib/api-error";
import { useAuth } from "./AuthProvider";
import { authApi } from "./auth.api";

function isAccountConflict(error: unknown): boolean {
  if (typeof error !== "object" || error === null || !("response" in error)) {
    return false;
  }

  const response = (error as { response?: { status?: unknown } }).response;
  return response?.status === 409;
}

export function RegisterPage() {
  const { register, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [codeRequested, setCodeRequested] = useState(false);
  const [emailAlreadyRegistered, setEmailAlreadyRegistered] = useState(false);

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/app", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  function showExistingAccount(error: unknown) {
    setCodeRequested(false);
    setEmailAlreadyRegistered(true);
    setOtp("");
    setPassword("");
    setConfirmPassword("");
    setSuccessMessage(null);
    setErrorMessage(
      getApiErrorMessage(
        error,
        "An account already exists for this email. Please sign in or reset your password.",
      ),
    );
  }

  async function requestCode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);
    setEmailAlreadyRegistered(false);
    setIsSubmitting(true);

    try {
      const response = await authApi.requestRegistrationOtp({
        email: email.trim().toLowerCase(),
      });

      setCodeRequested(true);
      setSuccessMessage(response.message);
    } catch (error) {
      if (isAccountConflict(error)) {
        showExistingAccount(error);
      } else {
        setErrorMessage(
          getApiErrorMessage(
            error,
            "Unable to send a verification code. Please try again later.",
          ),
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!codeRequested) {
      setErrorMessage("Request an email verification code first.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage("The passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        email: email.trim().toLowerCase(),
        otp: otp.trim(),
        password,
      });

      navigate("/app", { replace: true });
    } catch (error) {
      if (isAccountConflict(error)) {
        showExistingAccount(error);
      } else {
        setErrorMessage(
          getApiErrorMessage(
            error,
            "Account creation failed. Check the verification code and try again.",
          ),
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function resendCode() {
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsSubmitting(true);

    try {
      const response = await authApi.requestRegistrationOtp({
        email: email.trim().toLowerCase(),
      });

      setSuccessMessage(response.message);
      setOtp("");
    } catch (error) {
      if (isAccountConflict(error)) {
        showExistingAccount(error);
      } else {
        setErrorMessage(
          getApiErrorMessage(error, "Unable to resend the code."),
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  function changeEmail() {
    setCodeRequested(false);
    setEmailAlreadyRegistered(false);
    setOtp("");
    setPassword("");
    setConfirmPassword("");
    setErrorMessage(null);
    setSuccessMessage(null);
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

      <section className="login-card" aria-labelledby="register-title">
        <div className="login-card-topline">
          <span className="login-badge">
            <ShieldCheck size={14} /> EMAIL OTP REGISTRATION
          </span>
          <span className="login-lock">
            <KeyRound size={15} />
          </span>
        </div>

        <div className="login-heading">
          <h2 id="register-title">Create your account</h2>
          <p>
            {codeRequested
              ? `Enter the six-digit verification code sent to ${email}.`
              : "Create your AgentOps-OS account with your email address. We'll send you a verification code."}
          </p>
        </div>

        <form
          onSubmit={codeRequested ? createAccount : requestCode}
          className="login-form"
        >
          <div className="form-field">
            <label htmlFor="register-email">Email address</label>
            <div className="input-wrap">
              <Mail
                className="input-leading-icon"
                size={17}
                aria-hidden="true"
              />
              <TextInput
                id="register-email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  setEmailAlreadyRegistered(false);
                  setErrorMessage(null);
                }}
                required
                maxLength={320}
                disabled={isSubmitting || isLoading || codeRequested}
              />
            </div>
          </div>

          {codeRequested && (
            <>
              <div className="form-field">
                <label htmlFor="registration-otp">
                  Email verification code
                </label>
                <div className="input-wrap">
                  <KeyRound
                    className="input-leading-icon"
                    size={17}
                    aria-hidden="true"
                  />
                  <TextInput
                    id="registration-otp"
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    placeholder="Enter the six-digit code from your email"
                    value={otp}
                    onChange={(event) =>
                      setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
                    }
                    required
                    minLength={6}
                    maxLength={6}
                    pattern="[0-9]{6}"
                    disabled={isSubmitting || isLoading}
                  />
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="register-password">Password</label>
                <div className="input-wrap">
                  <LockKeyhole
                    className="input-leading-icon"
                    size={17}
                    aria-hidden="true"
                  />
                  <TextInput
                    id="register-password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="At least 12 characters"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    minLength={12}
                    maxLength={128}
                    disabled={isSubmitting || isLoading}
                    className="password-input"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                  </button>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="confirm-password">Confirm password</label>
                <div className="input-wrap">
                  <LockKeyhole
                    className="input-leading-icon"
                    size={17}
                    aria-hidden="true"
                  />
                  <TextInput
                    id="confirm-password"
                    type={showConfirmPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="Enter your password again"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    required
                    minLength={12}
                    maxLength={128}
                    disabled={isSubmitting || isLoading}
                    className="password-input"
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

              <p className="auth-form-hint">
                Passwords must contain 12–128 characters. The verification code
                is single-use and expires in 10 minutes. New accounts receive
                the Operator role.
              </p>
            </>
          )}

          {errorMessage && !emailAlreadyRegistered && (
            <div className="form-alert" role="alert">
              <span className="alert-dot" />
              {errorMessage}
            </div>
          )}

          {emailAlreadyRegistered && (
            <div className="auth-info-panel" role="alert">
              <strong>Email already registered</strong>
              <p>{errorMessage}</p>
              <p>
                <Link className="text-action" to="/login">
                  Sign in
                </Link>
                {" or "}
                <Link className="text-action" to="/forgot-password">
                  reset your password
                </Link>
                {" if you cannot access your account."}
              </p>
            </div>
          )}

          {successMessage && (
            <div className="auth-success" role="status">
              {successMessage}
              {codeRequested &&
                " Check your inbox and spam folder. The code can only be used once."}
            </div>
          )}

          <Button
            type="submit"
            size="lg"
            className="login-submit"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting ? (
              <>
                <span className="button-spinner" />
                {codeRequested ? "Creating account…" : "Sending code…"}
              </>
            ) : codeRequested ? (
              <>
                Create account <ArrowRight size={17} />
              </>
            ) : (
              <>
                Send verification code <ArrowRight size={17} />
              </>
            )}
          </Button>

          {codeRequested && (
            <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
              <button
                type="button"
                className="text-action"
                onClick={resendCode}
                disabled={isSubmitting || isLoading}
              >
                Resend code
              </button>
              <button
                type="button"
                className="text-action"
                onClick={changeEmail}
                disabled={isSubmitting || isLoading}
              >
                Change email
              </button>
            </div>
          )}
        </form>

        <div className="login-divider">
          <span /> <span>SECURE ACCESS</span> <span />
        </div>

        <p className="signup-prompt">
          Already have an account?{" "}
          <Link className="text-action signup-link" to="/login">
            Sign in
          </Link>
        </p>

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