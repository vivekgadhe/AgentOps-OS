import { useEffect, useState, type FormEvent } from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { Button } from "../../components/ui/Button";
import { TextInput } from "../../components/ui/TextInput";
import { AuthLayout } from "../../layouts/AuthLayout";
import { getApiErrorMessage } from "../../lib/api-error";
import { useAuth } from "./AuthProvider";
import { getRememberedEmail } from "./token-storage";

interface LoginLocationState {
  from?: {
    pathname?: string;
  };
}

export function LoginPage() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const routeState = location.state as LoginLocationState | null;
  const destination = routeState?.from?.pathname || "/app";

  const [email, setEmail] = useState(getRememberedEmail());
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(Boolean(getRememberedEmail()));
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) navigate(destination, { replace: true });
  }, [destination, isAuthenticated, navigate]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      await login(
        { email: email.trim().toLowerCase(), password },
        rememberMe,
      );
      navigate(destination, { replace: true });
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, "Sign-in failed. Please try again."),
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

      <section className="login-card" aria-labelledby="login-title">
        <div className="login-card-topline">
          <span className="login-badge">
            <ShieldCheck size={14} /> SECURE WORKSPACE
          </span>
          <span className="login-lock">
            <LockKeyhole size={15} />
          </span>
        </div>

        <div className="login-heading">
          <h2 id="login-title">Welcome back</h2>
          <p>Sign in to your workspace</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-field">
            <label htmlFor="email">Email</label>
            <div className="input-wrap">
              <Mail
                className="input-leading-icon"
                size={17}
                aria-hidden="true"
              />
              <TextInput
                id="email"
                type="email"
                name="email"
                autoComplete="username"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                maxLength={320}
                disabled={isSubmitting || isLoading}
              />
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="password">Password</label>
            <div className="input-wrap">
              <LockKeyhole
                className="input-leading-icon"
                size={17}
                aria-hidden="true"
              />
              <TextInput
                id="password"
                type={showPassword ? "text" : "password"}
                name="password"
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                maxLength={128}
                disabled={isSubmitting || isLoading}
                className="password-input"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                aria-pressed={showPassword}
              >
                {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </div>
          </div>

          <div className="login-options">
            <label className="remember-control">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
                disabled={isSubmitting || isLoading}
              />
              <span className="custom-checkbox" aria-hidden="true" />
              <span>Remember me</span>
            </label>

            <Link className="text-action" to="/forgot-password">
              Forgot password?
            </Link>
          </div>

          {errorMessage && (
            <div className="form-alert" role="alert">
              <span className="alert-dot" />
              {errorMessage}
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
                <span className="button-spinner" /> Signing in…
              </>
            ) : (
              <>
                Sign in <ArrowRight size={17} />
              </>
            )}
          </Button>
        </form>

        <div className="login-divider">
          <span />
          <span>SECURE ACCESS</span>
          <span />
        </div>

        <p className="signup-prompt">
          New to AgentOps-OS?{" "}
          <Link className="text-action signup-link" to="/register">
            Create an account
          </Link>
        </p>
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