import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { WorkflowTrendPoint } from "../../types/observability";

interface PerformanceChartsProps {
  data: WorkflowTrendPoint[];
  total: number;
  periodLabel: string;
}

export function PerformanceCharts({ data, total, periodLabel }: PerformanceChartsProps) {
  return (
    <section className="p4-card p4-chart-card">
      <div className="p4-section-heading">
        <div><span className="p4-kicker">EXECUTION TRENDS</span><h2>Workflow runs</h2><p>{periodLabel} · {total} workflow records returned by the API</p></div>
        <span className="p4-live-tag">Database-backed</span>
      </div>
      {total === 0 ? <div className="p4-empty">No workflow execution records were returned for this period.</div> : (
        <div className="p4-chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 12, left: -18, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#edf0f6" />
              <XAxis dataKey="date" tick={{ fill: "#8390a4", fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis allowDecimals={false} tick={{ fill: "#8390a4", fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ border: "1px solid #e4eaf3", borderRadius: 10, fontSize: 11 }} />
              <Legend wrapperStyle={{ fontSize: 10, paddingTop: 8 }} />
              <Bar dataKey="succeeded" name="Succeeded" stackId="runs" fill="#18b889" radius={[3, 3, 0, 0]} />
              <Bar dataKey="failed" name="Failed" stackId="runs" fill="#ef5267" />
              <Bar dataKey="cancelled" name="Cancelled" stackId="runs" fill="#9aa5b5" />
              <Bar dataKey="active" name="Pending / active" stackId="runs" fill="#4f8df7" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      <p className="p4-chart-note">The chart is grouped from the latest workflow records returned by the observability API. It does not invent missing dates or runs.</p>
    </section>
  );
}
