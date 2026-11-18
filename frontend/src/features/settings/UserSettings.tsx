import { useState, type FormEvent } from "react";
import { CheckCircle2, MailPlus, ShieldAlert, Users } from "lucide-react";
import { useAuth } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../../lib/api-error";
import { settingsService } from "../../services/settings.service";
import type { UserRole } from "../auth/auth.types";

export function UserSettings() {
  const { user } = useAuth();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<UserRole>("operator");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    setBusy(true);
    try {
      const result = await settingsService.createInvitation({ email: email.trim().toLowerCase(), role });
      setSuccess(`Invitation sent to ${result.email}. Verification expires ${new Date(result.expires_at).toLocaleString()}.`);
      setEmail("");
      setRole("operator");
    } catch (cause) {
      setError(getApiErrorMessage(cause, "Unable to create the invitation."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="p4-settings-grid">
      <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">CURRENT USER</span><h2>Account information</h2><p>The API exposes the current user profile, not a workspace-wide user directory.</p></div><Users size={22} /></div>
        <div className="p4-info-list"><div><span>Email</span><strong>{user?.email ?? "—"}</strong></div><div><span>Role</span><strong className="p4-role-pill">{user?.role ?? "Unknown"}</strong></div><div><span>Active</span><strong>{user?.is_active ? "Yes" : "No"}</strong></div></div>
        <div className="p4-capability-note"><ShieldAlert size={17} /><span>The current backend does not expose user listing, role-edit, deactivation or deletion endpoints. Those controls are intentionally not simulated here.</span></div>
      </section>
      <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">INVITATIONS</span><h2>Invite a team member</h2><p>Uses the existing administrator invitation API and email verification flow.</p></div><MailPlus size={22} /></div>
        {user?.role !== "admin" ? <div className="p4-empty p4-empty-compact">Only a workspace administrator can send managed invitations.</div> : <form className="p4-form" onSubmit={(event) => void submit(event)}>
          <label>Email address<input type="email" required maxLength={320} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="teammate@example.com" /></label>
          <label>Assigned role<select value={role} onChange={(event) => setRole(event.target.value as UserRole)}><option value="operator">Operator</option><option value="viewer">Viewer</option><option value="admin">Administrator</option></select></label>
          {error && <div className="p4-error-banner" role="alert">{error}</div>}
          {success && <div className="p4-success-banner" role="status"><CheckCircle2 size={16} />{success}</div>}
          <button className="p4-primary-button" type="submit" disabled={busy || !email.trim()}>{busy ? "Sending invitation…" : "Send invitation"}</button>
        </form>}
      </section>
    </div>
  );
}
