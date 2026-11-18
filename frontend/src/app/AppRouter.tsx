import { useLayoutEffect, type ReactNode } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { useAuth } from "../features/auth/AuthProvider";
import { ForgotPasswordPage } from "../features/auth/ForgotPasswordPage";
import { LoginPage } from "../features/auth/LoginPage";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { RegisterPage } from "../features/auth/RegisterPage";
import { WorkspaceHome } from "../pages/WorkspaceHome";

function ScrollToTopOnRouteChange() {
  const { pathname } = useLocation();

  useLayoutEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

function GuestRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="route-loading">Loading AgentOps-OS…</div>;
  if (isAuthenticated) return <Navigate to="/app" replace />;
  return <>{children}</>;
}

function NotFoundRoute() {
  return (
    <main className="not-found-page">
      <div className="not-found-code">404</div>
      <h1>Page not found</h1>
      <p>The page you requested is not part of this workspace.</p>
      <Link to="/app">Return to workspace</Link>
    </main>
  );
}

export function AppRouter() {
  return (
    <>
      <ScrollToTopOnRouteChange />
      <Routes>
        <Route path="/" element={<Navigate to="/app" replace />} />
        <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
        <Route path="/forgot-password" element={<GuestRoute><ForgotPasswordPage /></GuestRoute>} />
        <Route
          path="/app/*"
          element={
            <ProtectedRoute>
              <WorkspaceHome />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFoundRoute />} />
      </Routes>
    </>
  );
}
