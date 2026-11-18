import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Search, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

import { getApiErrorMessage } from '../../lib/api-error';
import { approvalsApi } from '../dashboard/dashboard.api';
import { formatDate, titleCase } from '../dashboard/format';

export function ApprovalList() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const query = useQuery({ queryKey: ['approvals'], queryFn: approvalsApi.list, refetchInterval: 15_000 });
  const approvals = query.data ?? [];
  const pending = approvals.filter((item) => item.status === 'pending');
  const filtered = useMemo(() => approvals.filter((item) => {
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    const term = search.trim().toLowerCase();
    const matchesSearch = !term || `${item.action_summary} ${item.tool_name} ${item.workflow_run_id}`.toLowerCase().includes(term);
    return matchesStatus && matchesSearch;
  }), [approvals, search, statusFilter]);

  return (
    <section className="phase2-page">
      <div className="phase2-page-heading"><div><span className="phase2-kicker">HUMAN-IN-THE-LOOP</span><h1>Approvals</h1><p>Review proposed actions and decide whether protected workflow steps may proceed.</p></div><div className="phase2-approval-counter"><strong>{pending.length}</strong><span>pending requests visible to you</span></div></div>
      {query.isError && <div className="phase2-alert error">{getApiErrorMessage(query.error, 'Unable to load approvals.')}</div>}
      {query.isLoading ? <div className="phase2-loading">Loading approval inbox…</div> : (
        <section className="phase2-panel phase2-table-panel">
          <div className="phase2-panel-heading"><div><h2>Approval inbox</h2><p>Admins see the workspace inbox; other roles see requests they created.</p></div></div>
          <div className="phase2-approval-filters"><label className="phase2-list-search"><Search size={15} /><input aria-label="Search approvals" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search proposed actions or tools…" /></label><select aria-label="Filter approval status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All statuses</option><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="executed">Executed</option><option value="expired">Expired</option><option value="cancelled">Cancelled</option></select></div>
          {filtered.length === 0 ? <div className="phase2-empty-state"><ShieldCheck size={26} /><strong>{approvals.length ? 'No matching approval requests' : 'No approval requests'}</strong><p>{approvals.length ? 'Try changing your search or status filter.' : 'When a workflow calls a server-registered tool that requires approval, its request appears here.'}</p></div> : (
            <div className="phase2-approval-list">{filtered.map((approval) => <Link className="phase2-approval-row" to={`/app/approvals/${approval.id}`} key={approval.id}>
              <span className="phase2-approval-symbol"><ShieldCheck size={18} /></span>
              <span className="phase2-approval-copy"><strong>{approval.action_summary}</strong><small>{approval.tool_name} · Requested {formatDate(approval.requested_at)}</small><small>Workflow {approval.workflow_run_id.slice(0, 8)} · Expires {formatDate(approval.expires_at)}</small></span>
              <span className={`phase2-status-badge ${approval.status}`}>{titleCase(approval.status)}</span><ArrowRight size={16} />
            </Link>)}</div>
          )}
        </section>
      )}
    </section>
  );
}
