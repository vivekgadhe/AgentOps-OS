import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock3, Plus, RefreshCw, Search } from 'lucide-react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';

import { Button } from '../../components/ui/Button';
import { getApiErrorMessage } from '../../lib/api-error';
import { dashboardApi } from '../dashboard/dashboard.api';
import { formatDate, formatDuration, titleCase } from '../dashboard/format';

export function WorkflowList() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get('search') ?? '';
  const query = useQuery({ queryKey: ['workflow-list'], queryFn: () => dashboardApi.workflows(365, 100), refetchInterval: 30_000 });
  const items = useMemo(() => {
    const normalized = search.trim().toLowerCase();
    if (!normalized) return query.data?.items ?? [];
    return (query.data?.items ?? []).filter((item) => `${item.goal} ${item.status} ${item.id}`.toLowerCase().includes(normalized));
  }, [query.data?.items, search]);

  return (
    <section className="phase2-page">
      <div className="phase2-page-heading"><div><span className="phase2-kicker">ORCHESTRATION</span><h1>Workflows</h1><p>Review saved workflow runs, dependency progress and execution outcomes.</p></div><div className="phase2-heading-actions"><Button variant="secondary" size="sm" onClick={() => void query.refetch()}><RefreshCw size={15} /> Refresh</Button><Link className="phase2-primary-link" to="/app/workflows/new"><Plus size={16} /> New Workflow</Link></div></div>
      {query.isError && <div className="phase2-alert error">{getApiErrorMessage(query.error, 'Unable to load workflow history.')}</div>}
      {query.isLoading ? <div className="phase2-loading">Loading workflow history…</div> : (
        <section className="phase2-panel phase2-table-panel">
          <div className="phase2-panel-heading"><div><h2>Workflow runs</h2><p>{query.data?.total ?? 0} records in the last 365 days · showing up to 100</p></div></div>
          <div className="phase2-list-search"><Search size={15} /><input aria-label="Filter workflow runs" value={search} onChange={(event) => setSearchParams(event.target.value ? { search: event.target.value } : {})} placeholder="Search workflow goal, status or run ID…" /></div>
          {!items.length ? <div className="phase2-empty-state"><Clock3 size={24} /><strong>{search ? 'No matching workflows' : 'No workflows yet'}</strong><p>{search ? 'Try a different search term.' : 'Create a workflow to see execution history here.'}</p>{!search && <Link className="phase2-primary-link" to="/app/workflows/new">Create workflow</Link>}</div> : (
            <div className="phase2-table-wrap"><table className="phase2-table"><thead><tr><th>Workflow goal</th><th>Status</th><th>Tasks</th><th>Duration</th><th>Created</th><th /></tr></thead><tbody>{items.map((item) => <tr key={item.id} onClick={() => navigate(`/app/workflows/${item.id}`)} tabIndex={0} onKeyDown={(event) => { if (event.key === 'Enter') navigate(`/app/workflows/${item.id}`); }}><td><strong>{item.goal}</strong><small className="phase2-subline">Run ID: {item.id.slice(0, 8)}</small></td><td><span className={`phase2-status-badge ${item.status}`}>{titleCase(item.status)}</span></td><td>{item.succeeded_task_count}/{item.task_count} succeeded{item.failed_task_count > 0 ? ` · ${item.failed_task_count} failed` : ''}</td><td>{formatDuration(item.duration_ms)}</td><td>{formatDate(item.created_at)}</td><td><span className="phase2-table-open">Open →</span></td></tr>)}</tbody></table></div>
          )}
        </section>
      )}
    </section>
  );
}
