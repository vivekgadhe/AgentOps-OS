import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ProviderUsageItem } from "../../types/observability";

interface ProviderAnalyticsProps { items: ProviderUsageItem[]; }

export function ProviderAnalytics({ items }: ProviderAnalyticsProps) {
  return (
    <section className="p4-card">
      <div className="p4-section-heading"><div><span className="p4-kicker">MODEL ROUTING</span><h2>Provider usage</h2><p>Recorded provider and model attempts</p></div></div>
      {items.length === 0 ? <div className="p4-empty p4-empty-compact">No provider telemetry is available for this period.</div> : <>
        <div className="p4-chart-wrap p4-provider-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={items.map((item) => ({ label: `${item.provider} · ${item.model}`, attempts: item.attempt_count }))} layout="vertical" margin={{ top: 3, right: 12, left: 12, bottom: 3 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#edf0f6" />
              <XAxis type="number" allowDecimals={false} tick={{ fill: "#8390a4", fontSize: 9 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="label" width={128} tick={{ fill: "#65738b", fontSize: 9 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ border: "1px solid #e4eaf3", borderRadius: 10, fontSize: 10 }} />
              <Bar dataKey="attempts" name="Attempts" fill="#765ee7" radius={[0, 5, 5, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="p4-data-table-wrap"><table className="p4-data-table"><thead><tr><th>Provider / model</th><th>Attempts</th><th>Success</th><th>Failures</th><th>Refusals</th><th>Avg latency</th></tr></thead>
          <tbody>{items.map((item) => <tr key={`${item.provider}:${item.model}`}><td><strong>{item.provider}</strong><small>{item.model}</small></td><td>{item.attempt_count}</td><td>{(item.success_rate * 100).toFixed(1)}%</td><td>{item.failure_count}</td><td>{item.refusal_count}</td><td>{item.average_duration_ms === null ? "—" : `${Math.round(item.average_duration_ms)} ms`}</td></tr>)}</tbody>
        </table></div>
      </>}
    </section>
  );
}
