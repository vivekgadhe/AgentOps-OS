import type { AgentUsageItem } from "../../types/observability";

interface AgentAnalyticsProps { items: AgentUsageItem[]; }

export function AgentAnalytics({ items }: AgentAnalyticsProps) {
  return (
    <section className="p4-card">
      <div className="p4-section-heading"><div><span className="p4-kicker">AGENT PERFORMANCE</span><h2>Agent generation metrics</h2><p>Agent-attributed LLM attempts reported by telemetry</p></div></div>
      {items.length === 0 ? <div className="p4-empty p4-empty-compact">No agent-attributed telemetry is available for this period.</div> : (
        <div className="p4-agent-metrics">{items.map((item) => <article className="p4-agent-metric" key={item.agent_name}>
          <div className="p4-agent-metric-title"><strong>{item.agent_name.replaceAll("_", " ")}</strong><span>{(item.success_rate * 100).toFixed(1)}% success</span></div>
          <div className="p4-progress-track"><span style={{ width: `${Math.max(0, Math.min(100, item.success_rate * 100))}%` }} /></div>
          <div className="p4-metric-meta"><span>{item.generation_attempts} attempts</span><span>{item.success_count} successful</span><span>{item.failure_count} failed</span><span>{item.refusal_count} refused</span></div>
          <div className="p4-metric-latency">Average latency: {item.average_duration_ms === null ? "Not recorded" : `${Math.round(item.average_duration_ms)} ms`}</div>
        </article>)}</div>
      )}
    </section>
  );
}
