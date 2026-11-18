import { useMemo, useState } from "react";
import { Activity, AlertTriangle, Clock3, RefreshCw, Workflow } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { analyticsService } from "../../services/analytics.service";
import type { DateRangeParams, WorkflowAnalyticsItem, WorkflowTrendPoint } from "../../types/observability";
import { getApiErrorMessage } from "../../lib/api-error";
import { AgentAnalytics } from "./AgentAnalytics";
import { EventExplorer } from "./EventExplorer";
import { PerformanceCharts } from "./PerformanceCharts";
import { ProviderAnalytics } from "./ProviderAnalytics";

function makeRange(days: number): DateRangeParams {
  const end = new Date();
  const start = new Date(end);
  start.setDate(start.getDate() - days);
  return { start_at: start.toISOString(), end_at: end.toISOString() };
}

function formatDuration(milliseconds: number | null): string {
  if (milliseconds === null) return "—";
  if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
  const seconds = milliseconds / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)} s`;
  const minutes = Math.floor(seconds / 60);
  return `${minutes}m ${Math.round(seconds % 60)}s`;
}

function localDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function toTrend(items: WorkflowAnalyticsItem[], days: number): WorkflowTrendPoint[] {
  const buckets = new Map<string, WorkflowTrendPoint>();
  const today = new Date();
  for (let offset = days - 1; offset >= 0; offset -= 1) {
    const date = new Date(today);
    date.setDate(today.getDate() - offset);
    const key = date.toLocaleDateString(undefined, { month: "short", day: "2-digit" });
    buckets.set(localDateKey(date), { date: key, succeeded: 0, failed: 0, cancelled: 0, active: 0 });
  }
  for (const item of items) {
    const key = localDateKey(new Date(item.created_at));
    const bucket = buckets.get(key);
    if (!bucket) continue;
    if (item.status === "succeeded") bucket.succeeded += 1;
    else if (item.status === "failed") bucket.failed += 1;
    else if (item.status === "cancelled") bucket.cancelled += 1;
    else bucket.active += 1;
  }
  return [...buckets.values()];
}

function MetricCard({ icon: Icon, label, value, detail, tone }: { icon: typeof Workflow; label: string; value: string; detail: string; tone: string }) {
  return <article className="p4-metric-card"><span className={`p4-metric-icon ${tone}`}><Icon size={18} /></span><strong className="p4-metric-value">{value}</strong><span className="p4-metric-label">{label}</span><small>{detail}</small></article>;
}

export function AnalyticsDashboard() {
  const [days, setDays] = useState(30);
  const [eventType, setEventType] = useState("");
  const [eventLimit, setEventLimit] = useState(25);
  const range = useMemo(() => makeRange(days), [days]);
  const queryKey = [range.start_at, range.end_at] as const;

  const overviewQuery = useQuery({ queryKey: ["analytics", "overview", ...queryKey], queryFn: () => analyticsService.getOverview(range) });
  const providerQuery = useQuery({ queryKey: ["analytics", "providers", ...queryKey], queryFn: () => analyticsService.getProviders(range) });
  const agentQuery = useQuery({ queryKey: ["analytics", "agents", ...queryKey], queryFn: () => analyticsService.getAgents(range) });
  const workflowQuery = useQuery({ queryKey: ["analytics", "workflows", ...queryKey], queryFn: () => analyticsService.getWorkflows({ ...range, limit: 100, offset: 0 }) });
  const eventQuery = useQuery({
    queryKey: ["analytics", "events", ...queryKey, eventType, eventLimit],
    queryFn: () => analyticsService.getEvents({ ...range, event_type: eventType || undefined, limit: eventLimit, offset: 0 }),
  });

  const overview = overviewQuery.data;
  const workflows = workflowQuery.data?.items ?? [];
  const trend = useMemo(() => toTrend(workflows, days), [workflows, days]);
  const failedOrRefused = (overview?.llm_failure_count ?? 0) + (overview?.llm_refusal_count ?? 0);
  const isRefreshing = [overviewQuery, providerQuery, agentQuery, workflowQuery, eventQuery].some((query) => query.isFetching);
  const firstError = [overviewQuery.error, providerQuery.error, agentQuery.error, workflowQuery.error, eventQuery.error].find(Boolean);

  const refreshAll = () => {
    void Promise.all([overviewQuery.refetch(), providerQuery.refetch(), agentQuery.refetch(), workflowQuery.refetch(), eventQuery.refetch()]);
  };

  return (
    <main className="p4-page">
      <header className="p4-page-heading">
        <div><span className="p4-kicker">OPERATIONS INTELLIGENCE</span><h1>Analytics &amp; Observability</h1><p>Monitor workflow execution, agent generation and configured AI provider performance using persisted telemetry.</p></div>
        <div className="p4-page-actions"><label className="p4-select-label">Reporting period<select value={days} onChange={(event) => { setDays(Number(event.target.value)); setEventLimit(25); }}><option value={7}>Last 7 days</option><option value={30}>Last 30 days</option><option value={90}>Last 90 days</option></select></label><button className="p4-secondary-button" type="button" onClick={refreshAll} disabled={isRefreshing}><RefreshCw size={14} className={isRefreshing ? "p4-spin" : ""} /> Refresh</button></div>
      </header>

      {firstError && <div className="p4-error-banner" role="alert">Some analytics could not be loaded: {getApiErrorMessage(firstError, "The observability API returned an error.")}</div>}

      <section className="p4-metric-grid" aria-label="Analytics overview">
        <MetricCard icon={Workflow} tone="violet" label="Total Runs" value={overview ? overview.workflow_count.toLocaleString() : "—"} detail="Workflow executions in selected period" />
        <MetricCard icon={Activity} tone="green" label="Success Rate" value={overview ? `${(overview.workflow_success_rate * 100).toFixed(1)}%` : "—"} detail={`${overview?.workflow_status_counts["succeeded"] ?? 0} successful workflow runs`} />
        <MetricCard icon={Clock3} tone="cyan" label="Average Execution Time" value={formatDuration(overview?.average_workflow_duration_ms ?? null)} detail="Completed workflow duration" />
        <MetricCard icon={AlertTriangle} tone="amber" label="LLM Attempts" value={overview ? overview.llm_attempt_count.toLocaleString() : "—"} detail={`${failedOrRefused} failures or refusals recorded`} />
      </section>

      <div className="p4-analytics-grid">
        <PerformanceCharts data={trend} total={workflowQuery.data?.total ?? 0} periodLabel={`Last ${days} days`} />
        <section className="p4-card p4-health-card">
          <div className="p4-section-heading"><div><span className="p4-kicker">MODEL GENERATION</span><h2>Generation outcomes</h2><p>Recorded LLM attempt results</p></div></div>
          <div className="p4-outcome-grid"><div><span>Successful</span><strong className="success">{overview?.llm_success_count ?? "—"}</strong></div><div><span>Failed</span><strong className="failed">{overview?.llm_failure_count ?? "—"}</strong></div><div><span>Refused</span><strong className="refused">{overview?.llm_refusal_count ?? "—"}</strong></div></div>
          <div className="p4-health-row"><span>LLM success rate</span><strong>{overview ? `${(overview.llm_success_rate * 100).toFixed(1)}%` : "—"}</strong></div>
          <div className="p4-health-row"><span>Average generation latency</span><strong>{formatDuration(overview?.average_llm_duration_ms ?? null)}</strong></div>
          <div className="p4-data-note">Token totals and cost are not shown: the current API does not provide a validated aggregate usage or billing measure.</div>
        </section>
        <ProviderAnalytics items={providerQuery.data?.items ?? []} />
        <AgentAnalytics items={agentQuery.data?.items ?? []} />
      </div>

      <EventExplorer
        items={eventQuery.data?.items ?? []}
        total={eventQuery.data?.total ?? 0}
        isLoading={eventQuery.isFetching}
        eventType={eventType}
        onEventTypeChange={(value) => { setEventType(value); setEventLimit(25); }}
        onLoadMore={() => setEventLimit((current) => Math.min(100, current + 25))}
        hasMore={(eventQuery.data?.items.length ?? 0) < (eventQuery.data?.total ?? 0) && eventLimit < 100}
      />

      <p className="p4-footnote">All reported data is scoped by the authenticated backend account. Workflow charts use up to 100 records returned by the workflow analytics endpoint; telemetry event history is separately paginated.</p>
    </main>
  );
}
