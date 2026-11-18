import type { WorkflowAnalyticsItem } from './dashboard.types';

const SERIES = [
  { key: 'succeeded', label: 'Succeeded', color: '#16b981' },
  { key: 'active', label: 'Active', color: '#4285f4' },
  { key: 'failed', label: 'Failed', color: '#ef476f' },
] as const;

function dayKey(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function buildDays(items: WorkflowAnalyticsItem[]) {
  const today = new Date();
  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today.getFullYear(), today.getMonth(), today.getDate() - (6 - index));
    return { date, key: dayKey(date), label: new Intl.DateTimeFormat(undefined, { month: 'short', day: '2-digit' }).format(date) };
  });
  const counts = new Map<string, { succeeded: number; active: number; failed: number }>();
  for (const day of days) counts.set(day.key, { succeeded: 0, active: 0, failed: 0 });
  for (const item of items) {
    const created = new Date(item.created_at);
    if (Number.isNaN(created.getTime())) continue;
    const bucket = counts.get(dayKey(created));
    if (!bucket) continue;
    if (item.status === 'succeeded') bucket.succeeded += 1;
    else if (item.status === 'failed') bucket.failed += 1;
    else if (['running', 'planning', 'pending', 'awaiting_approval'].includes(item.status)) bucket.active += 1;
  }
  return days.map((day) => ({ ...day, ...counts.get(day.key)! }));
}

export function WorkflowChart({ workflows, isUnavailable = false }: { workflows: WorkflowAnalyticsItem[]; isUnavailable?: boolean }) {
  const days = buildDays(workflows);
  const maximum = Math.max(1, ...days.flatMap((day) => SERIES.map((series) => day[series.key])));
  const chart = { width: 640, height: 230, left: 36, right: 14, top: 14, bottom: 34 };
  const plotWidth = chart.width - chart.left - chart.right;
  const plotHeight = chart.height - chart.top - chart.bottom;
  const xFor = (index: number) => chart.left + (days.length <= 1 ? plotWidth / 2 : (index / (days.length - 1)) * plotWidth);
  const yFor = (value: number) => chart.top + plotHeight - (value / maximum) * plotHeight;
  const pathFor = (key: typeof SERIES[number]['key']) => days.map((day, index) => `${index === 0 ? 'M' : 'L'} ${xFor(index).toFixed(1)} ${yFor(day[key]).toFixed(1)}`).join(' ');

  return (
    <section className="phase2-panel phase2-chart-panel">
      <div className="phase2-panel-heading">
        <div><span className="phase2-kicker">EXECUTION OVERVIEW</span><h2>Workflow Runs</h2></div>
        <span className="phase2-period-pill">Last 7 days</span>
      </div>
      {isUnavailable ? (
        <div className="phase2-chart-empty">Workflow trend data is unavailable because the observability API could not be reached.</div>
      ) : workflows.length === 0 ? (
        <div className="phase2-chart-empty">No workflow runs were returned for this period.</div>
      ) : (
        <div className="phase2-line-chart-wrap">
          <svg className="phase2-line-chart" viewBox={`0 0 ${chart.width} ${chart.height}`} role="img" aria-label="Workflow runs by creation date and status over the last seven days">
            {[0, 0.25, 0.5, 0.75, 1].map((fraction) => {
              const value = Math.round(maximum * fraction);
              const y = yFor(value);
              return <g key={fraction}><line x1={chart.left} y1={y} x2={chart.width - chart.right} y2={y} className="chart-grid-line" /><text x={chart.left - 10} y={y + 4} textAnchor="end" className="chart-axis-label">{value}</text></g>;
            })}
            {SERIES.map((series) => <g key={series.key}>
              <path d={pathFor(series.key)} fill="none" stroke={series.color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
              {days.map((day, index) => <circle key={`${series.key}-${day.key}`} cx={xFor(index)} cy={yFor(day[series.key])} r="3.4" fill={series.color} stroke="#fff" strokeWidth="1.5"><title>{`${day.label}: ${series.label} ${day[series.key]}`}</title></circle>)}
            </g>)}
            {days.map((day, index) => <text key={day.key} x={xFor(index)} y={chart.height - 8} textAnchor="middle" className="chart-axis-label">{day.label}</text>)}
          </svg>
          <div className="phase2-chart-legend">{SERIES.map((series) => <span key={series.key}><i style={{ background: series.color }} />{series.label}</span>)}</div>
        </div>
      )}
      <div className="phase2-chart-footnote">Daily totals group actual workflow records by creation date and current status. Active includes pending, planning, running and awaiting-approval runs. The API request is capped at 100 records.</div>
    </section>
  );
}
