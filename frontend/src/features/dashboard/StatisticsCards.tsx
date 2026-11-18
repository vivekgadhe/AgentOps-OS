import { FileText, GitBranch, ShieldAlert, Users } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface Statistic {
  label: string;
  value: number | null;
  caption: string;
  icon: LucideIcon;
  tone: string;
  unavailable?: boolean;
}

export function StatisticsCards({
  activeWorkflows,
  runningAgentCount,
  runningTaskCount,
  pendingApprovals,
  knowledgeDocuments,
}: {
  activeWorkflows: number | null;
  runningAgentCount: number | null;
  runningTaskCount: number | null;
  pendingApprovals: number | null;
  knowledgeDocuments: number | null;
}) {
  const runningCaption = runningTaskCount === null
    ? 'Live agent inventory is not exposed by the current API.'
    : `${runningTaskCount.toLocaleString()} workflow task step${runningTaskCount === 1 ? '' : 's'} currently running; separate agent count unavailable.`;

  const statistics: Statistic[] = [
    { label: 'Active Workflows', value: activeWorkflows, caption: 'Pending, planning, running or awaiting approval', icon: GitBranch, tone: 'violet' },
    { label: 'Running Agents', value: runningAgentCount, caption: runningCaption, icon: Users, tone: 'cyan', unavailable: true },
    { label: 'Pending Approvals', value: pendingApprovals, caption: 'Approval requests visible to your account', icon: ShieldAlert, tone: 'red' },
    { label: 'Knowledge Documents', value: knowledgeDocuments, caption: 'Documents indexed in your knowledge base', icon: FileText, tone: 'green' },
  ];

  return (
    <div className="phase2-stat-grid">
      {statistics.map(({ label, value, caption, icon: Icon, tone, unavailable }) => (
        <article className="phase2-stat-card" key={label}>
          <div className={`phase2-stat-icon ${tone}`}><Icon size={19} /></div>
          <div className="phase2-stat-value">{value === null ? '—' : value.toLocaleString()}</div>
          <div className="phase2-stat-label">{label}</div>
          <p>{caption}</p>
          {unavailable && <span className="phase2-stat-footnote">Not exposed by API</span>}
        </article>
      ))}
    </div>
  );
}
