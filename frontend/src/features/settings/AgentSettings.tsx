import { Bot, FileSearch, FileText, Info } from "lucide-react";

const agents = [
  { name: "Analysis Agent", description: "Answers questions using owner-scoped knowledge retrieval and the configured generation provider.", endpoint: "POST /api/v1/knowledge/query", icon: FileSearch },
  { name: "Report Agent", description: "Generates a structured report grounded in retrieved document passages.", endpoint: "POST /api/v1/knowledge/report", icon: FileText },
];

export function AgentSettings() {
  return (
    <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">AGENT CAPABILITIES</span><h2>Available knowledge agents</h2><p>Capabilities confirmed by the current backend API.</p></div><Bot size={22} /></div>
      <div className="p4-settings-entity-list">{agents.map(({ name, description, endpoint, icon: Icon }) => <article className="p4-settings-entity" key={name}><span className="p4-settings-entity-icon"><Icon size={19} /></span><div><strong>{name}</strong><p>{description}</p><code>{endpoint}</code></div><span className="p4-status-chip is-readonly">API available</span></article>)}</div>
      <div className="p4-capability-note"><Info size={17} /><span>The current backend does not expose agent discovery, per-agent enable/disable, prompt editing or runtime configuration endpoints. Agent cards are informational; no fake configuration controls are shown.</span></div>
    </section>
  );
}
