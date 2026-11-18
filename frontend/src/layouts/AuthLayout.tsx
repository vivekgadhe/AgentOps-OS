import type { ReactNode } from "react";

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <main className="auth-shell">
      <div className="auth-ambient auth-ambient-one" />
      <div className="auth-ambient auth-ambient-two" />
      <div className="auth-grid" />
      <img className="auth-waves" src="/auth-waves.svg" alt="" aria-hidden="true" />
      <div className="auth-content">{children}</div>
      <div className="auth-footer">AGENTOPS-OS <span>•</span> INTELLIGENT WORKFLOW INFRASTRUCTURE</div>
    </main>
  );
}
