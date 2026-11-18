import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, CircleAlert, Monitor, ShieldCheck, UserRound } from "lucide-react";
import { settingsService } from "../../services/settings.service";
import type { AuthUser } from "../auth/auth.types";

export function GeneralSettings({ user }: { user: AuthUser | null }) {
  const readiness = useQuery({ queryKey: ["settings", "readiness"], queryFn: settingsService.getReadiness, refetchInterval: 30_000 });
  return (
    <div className="p4-settings-grid">
      <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">WORKSPACE PROFILE</span><h2>General information</h2><p>Account and workspace information returned by the authenticated session.</p></div><UserRound size={22} /></div>
        <div className="p4-info-list"><div><span>Signed-in account</span><strong>{user?.email ?? "—"}</strong></div><div><span>Workspace role</span><strong className="p4-role-pill">{user?.role ?? "Unknown"}</strong></div><div><span>Account status</span><strong>{user?.is_active ? "Active" : "Inactive"}</strong></div><div><span>User ID</span><code>{user?.id ?? "Not available"}</code></div></div>
      </section>
      <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">SERVICE HEALTH</span><h2>Backend connection</h2><p>Live readiness probe and database connectivity.</p></div><Monitor size={22} /></div>
        {readiness.isPending ? <div className="p4-inline-status">Checking service readiness…</div> : readiness.isError ? <div className="p4-status-panel is-error"><CircleAlert size={18} /><div><strong>Readiness check failed</strong><span>The health endpoint could not be reached.</span></div></div> : <div className="p4-status-panel is-success"><CheckCircle2 size={18} /><div><strong>{readiness.data.status === "ok" ? "Application ready" : "Application unavailable"}</strong><span>API status: {readiness.data.status} · Database: {readiness.data.db}</span></div></div>}
      </section>
      <section className="p4-card p4-settings-wide"><div className="p4-section-heading"><div><span className="p4-kicker">ACCOUNT SECURITY</span><h2>Session and permissions</h2><p>Authentication and access rules are enforced by the backend.</p></div><ShieldCheck size={22} /></div><div className="p4-capability-grid"><div><strong>Authenticated API access</strong><span>Requests use the current bearer token.</span></div><div><strong>Owner-scoped records</strong><span>Knowledge, memory, workflow and telemetry data are scoped on the server.</span></div><div><strong>Role-based actions</strong><span>Administrative operations are restricted by backend role checks.</span></div></div></section>
    </div>
  );
}
