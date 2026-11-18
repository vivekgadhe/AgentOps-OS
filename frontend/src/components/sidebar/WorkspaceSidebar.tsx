import {
  Activity,
  Brain,
  BrainCircuit,
  CheckCircle2,
  Database,
  LayoutDashboard,
  LogOut,
  MailPlus,
  Settings,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import type { AuthUser } from "../../features/auth/auth.types";

interface NavigationItem {
  label: string;
  icon: LucideIcon;
  route?: string;
  adminOnly?: boolean;
  enabled?: boolean;
}

const navigation: NavigationItem[] = [
  { label: "Dashboard", icon: LayoutDashboard, route: "/app", enabled: true },
  { label: "Workflows", icon: Workflow, route: "/app/workflows", enabled: true },
  { label: "Agents", icon: BrainCircuit, route: "/app/agents", enabled: true },
  { label: "Knowledge", icon: Database, route: "/app/knowledge", enabled: true },
  { label: "Memory", icon: Brain, route: "/app/memory", enabled: true },
  { label: "Runs", icon: Activity, route: "/app/runs", enabled: true },
  { label: "Approvals", icon: CheckCircle2, route: "/app/approvals", enabled: true },
  { label: "Analytics", icon: Activity, route: "/app/analytics", enabled: true },
  { label: "Settings", icon: Settings, route: "/app/settings", enabled: true },
  { label: "Invitations", icon: MailPlus, route: "/app/invitations", adminOnly: true, enabled: true },
];

interface WorkspaceSidebarProps {
  user: AuthUser | null;
  pendingApprovalCount: number;
  onLogout: () => void;
}

export function WorkspaceSidebar({ user, pendingApprovalCount, onLogout }: WorkspaceSidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const visibleNavigation = navigation.filter((item) => !item.adminOnly || user?.role === "admin");

  return (
    <aside className="workspace-sidebar">
      <div className="workspace-brand"><span className="brand-mark brand-mark-small"><BrainCircuit size={18} /></span><span>AgentOps-OS</span></div>
      <div className="sidebar-section-label">WORKSPACE</div>
      <nav className="workspace-nav" aria-label="Workspace navigation">
        {visibleNavigation.map(({ label, icon: Icon, route, enabled }) => {
          const active = route !== undefined && (route === "/app" ? location.pathname === "/app" : location.pathname.startsWith(route));
          return (
            <button className={`workspace-nav-item${active ? " is-active" : ""}`} type="button" disabled={!enabled} key={label} onClick={() => route && navigate(route)} title={enabled ? label : `${label} is part of a later frontend package`}>
              <Icon size={17} /><span>{label}</span>
              {label === "Approvals" && pendingApprovalCount > 0 && <span className="nav-count-badge">{pendingApprovalCount > 99 ? "99+" : pendingApprovalCount}</span>}
              {!enabled && <span className="nav-soon">Soon</span>}
            </button>
          );
        })}
      </nav>
      <div className="sidebar-bottom">
        <div className="sidebar-status"><span /> Backend connection configured</div>
        <button className="logout-button" type="button" onClick={onLogout}><LogOut size={16} />Sign out</button>
      </div>
    </aside>
  );
}
