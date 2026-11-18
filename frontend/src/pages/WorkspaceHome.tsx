import { Route, Routes, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { useAuth } from "../features/auth/AuthProvider";
import { InvitationManagement } from "../features/invitations/InvitationManagement";
import { Dashboard } from "../features/dashboard/Dashboard";
import { dashboardApi } from "../features/dashboard/dashboard.api";
import { WorkflowList } from "../features/workflows/WorkflowList";
import { WorkflowBuilder } from "../features/workflows/WorkflowBuilder";
import { WorkflowExecution } from "../features/workflows/WorkflowExecution";
import { ApprovalList } from "../features/approvals/ApprovalList";
import { ApprovalDetails } from "../features/approvals/ApprovalDetails";
import { KnowledgePage } from "../features/knowledge/KnowledgePage";
import { AgentsPage } from "../features/agents/AgentsPage";
import { MemoryPage } from "../features/memory/MemoryPage";
import { AnalyticsDashboard } from "../features/analytics/AnalyticsDashboard";
import { SettingsDashboard } from "../features/settings/SettingsDashboard";
import { DashboardLayout } from "../layouts/DashboardLayout";

function WorkspaceNotFound() {
  return <section className="phase2-page"><div className="phase2-empty-state"><strong>Workspace page not found</strong><p>This page is not included in the current frontend package.</p></div></section>;
}

export function WorkspaceHome() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const approvalsQuery = useQuery({ queryKey: ["approvals"], queryFn: dashboardApi.approvals, refetchInterval: 30_000 });
  const pendingApprovalCount = approvalsQuery.data?.filter((approval) => approval.status === "pending").length ?? 0;
  const currentLabel = location.pathname.includes("/approvals") ? "Approvals"
    : location.pathname.includes("/runs") ? "Runs"
      : location.pathname.includes("/workflows") ? "Workflows"
        : location.pathname.includes("/invitations") ? "Invitations"
          : location.pathname.includes("/knowledge") ? "Knowledge"
            : location.pathname.includes("/agents") ? "Agents"
              : location.pathname.includes("/memory") ? "Memory"
                : location.pathname.includes("/analytics") ? "Analytics"
                  : location.pathname.includes("/settings") ? "Settings" : "Dashboard";

  return (
    <DashboardLayout user={user} currentLabel={currentLabel} pendingApprovalCount={pendingApprovalCount} onLogout={logout}>
      <Routes>
        <Route index element={<Dashboard />} />
        <Route path="workflows" element={<WorkflowList />} />
        <Route path="runs" element={<WorkflowList />} />
        <Route path="workflows/new" element={<WorkflowBuilder />} />
        <Route path="workflows/:workflowId" element={<WorkflowExecution />} />
        <Route path="approvals" element={<ApprovalList />} />
        <Route path="approvals/:approvalId" element={<ApprovalDetails />} />
        <Route path="invitations" element={<InvitationManagement />} />
        <Route path="knowledge" element={<KnowledgePage />} />
        <Route path="agents" element={<AgentsPage />} />
        <Route path="memory" element={<MemoryPage />} />
        <Route path="analytics" element={<AnalyticsDashboard />} />
        <Route path="settings" element={<SettingsDashboard />} />
        <Route path="*" element={<WorkspaceNotFound />} />
      </Routes>
    </DashboardLayout>
  );
}
