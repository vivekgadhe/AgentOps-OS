import { KeyRound, LockKeyhole, ShieldCheck } from "lucide-react";

const rules = [
  { title: "Role-based API authorization", detail: "Admin, operator and viewer roles are checked by backend route dependencies and service-level authorization." },
  { title: "Protected tool approvals", detail: "Approval requirements are declared in trusted server-side ToolDefinition registrations. Workflow input cannot enable or disable approval policy." },
  { title: "Credential encryption", detail: "Hosted provider credentials are encrypted before being persisted. The provider API never returns stored API keys." },
  { title: "Owner-scoped observability", detail: "Workflow and telemetry analytics are filtered to the authenticated account by the backend." },
];

export function SecuritySettings() {
  return (
    <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">SECURITY CONTROLS</span><h2>Authorization &amp; protection</h2><p>Current backend security behaviours. These are read-only because policy mutation endpoints are not available.</p></div><ShieldCheck size={22} /></div>
      <div className="p4-security-list">{rules.map((rule, index) => <article className="p4-security-row" key={rule.title}><span className="p4-security-icon">{index === 2 ? <KeyRound size={18} /> : <LockKeyhole size={18} />}</span><div><strong>{rule.title}</strong><p>{rule.detail}</p></div><span className="p4-status-chip is-readonly">Enforced by API</span></article>)}</div>
      <div className="p4-capability-note"><ShieldCheck size={17} /><span>Approval decisions are managed in the Approvals workspace. The current API does not provide editable approval-policy rules, global authorization settings or session-policy controls.</span></div>
    </section>
  );
}
