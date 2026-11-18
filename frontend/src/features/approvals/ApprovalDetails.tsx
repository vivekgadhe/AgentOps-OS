import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Clock3, ExternalLink, ShieldCheck } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

import { getApiErrorMessage } from '../../lib/api-error';
import { useAuth } from '../auth/AuthProvider';
import { approvalsApi } from '../dashboard/dashboard.api';
import { formatDate, titleCase } from '../dashboard/format';
import { ApprovalActions } from './ApprovalActions';

export function ApprovalDetails() {
  const { approvalId = '' } = useParams();
  const { user } = useAuth();
  const query = useQuery({ queryKey: ['approval', approvalId], queryFn: () => approvalsApi.get(approvalId), enabled: Boolean(approvalId) });
  const approval = query.data;

  return (
    <section className="phase2-page"><Link to="/app/approvals" className="phase2-back-link"><ArrowLeft size={14} /> Approval inbox</Link>
      {query.isLoading && <div className="phase2-loading">Loading approval details…</div>}
      {query.isError && <div className="phase2-alert error">{getApiErrorMessage(query.error, 'Approval request could not be found or is not accessible.')}</div>}
      {approval && <>
        <div className="phase2-page-heading"><div><span className="phase2-kicker">APPROVAL REVIEW</span><h1>Review proposed action</h1><p>{approval.action_summary}</p></div><span className={`phase2-status-badge ${approval.status}`}>{titleCase(approval.status)}</span></div>
        <div className="phase2-approval-detail-grid">
          <section className="phase2-panel"><div className="phase2-panel-heading"><div><span className="phase2-kicker">PROPOSED ACTION</span><h2><ShieldCheck size={17} /> {approval.tool_name}</h2></div></div>
            <p className="phase2-approval-summary">{approval.action_summary}</p><h3 className="phase2-subheading">Proposed action details</h3>
            <pre className="phase2-code-block">{JSON.stringify(approval.input_snapshot, null, 2)}</pre>
            <p className="phase2-chart-footnote">The backend redacts common secret-like input keys before storing this approval snapshot.</p>
            <div className="phase2-approval-meta"><span>Requested <strong>{formatDate(approval.requested_at)}</strong></span><span>Expires <strong>{formatDate(approval.expires_at)}</strong></span><span>Decided <strong>{formatDate(approval.decided_at)}</strong></span><span>Requester ID <strong>{approval.requester_user_id}</strong></span>{approval.decided_by_user_id && <span>Decided by <strong>{approval.decided_by_user_id}</strong></span>}</div>
            {approval.decision_reason && <div className="phase2-decision-reason"><strong>Decision reason</strong><p>{approval.decision_reason}</p></div>}
          </section>
          <aside className="phase2-side-stack">
            <section className="phase2-panel"><div className="phase2-panel-heading"><div><span className="phase2-kicker">DECISION</span><h2>Approval actions</h2></div></div><ApprovalActions approval={approval} currentUserId={user?.id ?? ''} role={user?.role ?? ''} onComplete={() => { void query.refetch(); }} /></section>
            <section className="phase2-panel"><div className="phase2-panel-heading"><h2>Related records</h2></div><Link className="phase2-related-link" to={`/app/workflows/${approval.workflow_run_id}`}><span><Clock3 size={15} /> Workflow execution</span><ExternalLink size={14} /></Link><div className="phase2-chart-footnote">Workflow run: {approval.workflow_run_id}</div><div className="phase2-chart-footnote">Task run: {approval.task_run_id}</div></section>
          </aside>
        </div>
      </>}
    </section>
  );
}
