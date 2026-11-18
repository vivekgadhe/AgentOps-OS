import { ArrowUpRight, FileText, GitBranch, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

import type { ApprovalItem, KnowledgeDocument, WorkflowAnalyticsItem } from './dashboard.types';
import { formatDate, titleCase } from './format';

type ActivityItem = {
  id: string;
  kind: 'workflow' | 'approval' | 'document';
  label: string;
  status: string;
  createdAt: string;
  href: string | null;
};

export function RecentActivity({
  workflows,
  approvals,
  documents,
}: {
  workflows: WorkflowAnalyticsItem[];
  approvals: ApprovalItem[];
  documents: KnowledgeDocument[];
}) {
  const items: ActivityItem[] = [
    ...workflows.map((item) => ({
      id: item.id,
      kind: 'workflow' as const,
      label: item.goal,
      status: item.status,
      createdAt: item.created_at,
      href: `/app/workflows/${item.id}`,
    })),
    ...approvals.map((item) => ({
      id: item.id,
      kind: 'approval' as const,
      label: item.action_summary,
      status: item.status,
      createdAt: item.requested_at,
      href: `/app/approvals/${item.id}`,
    })),
    ...documents.map((item) => ({
      id: item.id,
      kind: 'document' as const,
      label: item.filename,
      status: 'processed',
      createdAt: item.created_at,
      href: null,
    })),
  ].sort((first, second) => new Date(second.createdAt).getTime() - new Date(first.createdAt).getTime()).slice(0, 7);

  return (
    <section className="phase2-panel phase2-activity-panel">
      <div className="phase2-panel-heading">
        <div><span className="phase2-kicker">WORKSPACE FEED</span><h2>Recent Activity</h2></div>
        <Link className="phase2-inline-link" to="/app/workflows">View all <ArrowUpRight size={14} /></Link>
      </div>
      {items.length === 0 ? (
        <p className="phase2-muted">No workflow, approval or document activity has been recorded yet.</p>
      ) : (
        <div className="phase2-activity-list">
          {items.map((item) => {
            const Icon = item.kind === 'workflow' ? GitBranch : item.kind === 'approval' ? ShieldCheck : FileText;
            const content = (
              <>
                <span className={`phase2-activity-icon ${item.kind}`}><Icon size={16} /></span>
                <span className="phase2-activity-copy"><strong>{item.label}</strong><small>{item.kind === 'workflow' ? 'Workflow run' : item.kind === 'approval' ? 'Approval request' : 'Knowledge document'} · {formatDate(item.createdAt)}</small></span>
                <span className={`phase2-status-badge ${item.status}`}>{titleCase(item.status)}</span>
              </>
            );
            return item.href ? (
              <Link className="phase2-activity-item" to={item.href} key={`${item.kind}-${item.id}`}>{content}</Link>
            ) : (
              <div className="phase2-activity-item" key={`${item.kind}-${item.id}`}>{content}</div>
            );
          })}
        </div>
      )}
      <div className="phase2-chart-footnote">Activity is assembled from actual workflow, approval and knowledge-document APIs. Task-level event logs are not exposed by the current backend.</div>
    </section>
  );
}
