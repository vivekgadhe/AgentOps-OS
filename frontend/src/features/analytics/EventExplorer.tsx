import { useState } from "react";
import { ChevronDown, ChevronUp, Search } from "lucide-react";
import type { TelemetryEvent } from "../../types/observability";

interface EventExplorerProps {
  items: TelemetryEvent[];
  total: number;
  isLoading: boolean;
  eventType: string;
  onEventTypeChange: (value: string) => void;
  onLoadMore: () => void;
  hasMore: boolean;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

export function EventExplorer({ items, total, isLoading, eventType, onEventTypeChange, onLoadMore, hasMore }: EventExplorerProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  return (
    <section className="p4-card p4-events-card">
      <div className="p4-section-heading"><div><span className="p4-kicker">OBSERVABILITY LOG</span><h2>Execution events</h2><p>{total} telemetry events available in the selected period. Event metadata is owner-scoped.</p></div>
        <label className="p4-select-label">Event type<select value={eventType} onChange={(event) => onEventTypeChange(event.target.value)}><option value="">All event types</option><option value="llm_attempt">LLM attempt</option></select></label>
      </div>
      {isLoading && items.length === 0 ? <div className="p4-empty">Loading telemetry events…</div> : items.length === 0 ? <div className="p4-empty">No telemetry events match this filter.</div> : (
        <div className="p4-event-list">{items.map((event) => <article className="p4-event-row" key={event.id}>
          <div className="p4-event-main"><span className={`p4-outcome-dot ${event.outcome}`} /><div className="p4-event-copy"><strong>{event.agent_name || event.component} · {event.provider}/{event.model}</strong><span>{event.event_type} · {event.component} · {formatDate(event.created_at)}</span></div><span className={`p4-outcome ${event.outcome}`}>{event.outcome}</span><button className="p4-icon-button" type="button" aria-label={expandedId === event.id ? "Hide event details" : "Show event details"} onClick={() => setExpandedId(expandedId === event.id ? null : event.id)}>{expandedId === event.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}</button></div>
          <div className="p4-event-stats"><span>{Math.round(event.duration_ms)} ms</span><span>{event.error_type ? `Error: ${event.error_type}` : "No error type recorded"}</span><span>{event.workflow_run_id ? `Run ${event.workflow_run_id.slice(0, 8)}` : "No workflow run"}</span></div>
          {expandedId === event.id && <div className="p4-event-details"><div><strong>Request ID</strong><code>{event.request_id || "Not recorded"}</code></div><div><strong>Input tokens</strong><span>{event.input_tokens ?? "Not recorded"}</span></div><div><strong>Output tokens</strong><span>{event.output_tokens ?? "Not recorded"}</span></div><div><strong>Safe attributes</strong><pre>{JSON.stringify(event.attributes, null, 2)}</pre></div></div>}
        </article>)}</div>
      )}
      <div className="p4-table-footer"><span>Showing {items.length} of {total} events</span>{hasMore && <button className="p4-secondary-button" type="button" onClick={onLoadMore} disabled={isLoading}><Search size={13} /> Load more</button>}</div>
      <p className="p4-chart-note">Prompts and model response content are not included in telemetry. Token counts are shown only when the backend recorded them; no token-cost estimates are derived here.</p>
    </section>
  );
}
