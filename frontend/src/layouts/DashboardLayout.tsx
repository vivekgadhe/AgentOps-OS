import type { ReactNode } from "react";

import type { AuthUser } from "../features/auth/auth.types";
import { WorkspaceNavbar } from "../components/navbar/WorkspaceNavbar";
import { WorkspaceSidebar } from "../components/sidebar/WorkspaceSidebar";

interface DashboardLayoutProps {
  user: AuthUser | null;
  currentLabel: string;
  pendingApprovalCount: number;
  onLogout: () => void;
  children: ReactNode;
}

export function DashboardLayout({ user, currentLabel, pendingApprovalCount, onLogout, children }: DashboardLayoutProps) {
  return (
    <div className="workspace-shell">
      <WorkspaceSidebar user={user} pendingApprovalCount={pendingApprovalCount} onLogout={onLogout} />
      <main className="workspace-main">
        <WorkspaceNavbar user={user} currentLabel={currentLabel} />
        {children}
      </main>
    </div>
  );
}
