import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Plus, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '../../components/ui/Button';
import { getApiErrorMessage } from '../../lib/api-error';
import { dashboardApi } from './dashboard.api';
import { RecentActivity } from './RecentActivity';
import { StatisticsCards } from './StatisticsCards';
import { WorkflowChart } from './WorkflowChart';

const ACTIVE_STATUSES = ['pending', 'planning', 'running', 'awaiting_approval'];

export function Dashboard() {
  const overviewQuery = useQuery({
    queryKey: ['dashboard', 'overview', 'all-time'],
    queryFn: () => dashboardApi.overview(36_500),
    refetchInterval: 30_000,
  });
  const workflowQuery = useQuery({
    queryKey: ['dashboard', 'workflows', '30-days'],
    queryFn: () => dashboardApi.workflows(30, 100),
    refetchInterval: 30_000,
  });
  const approvalQuery = useQuery({
    queryKey: ['dashboard', 'approvals'],
    queryFn: dashboardApi.approvals,
    refetchInterval: 30_000,
  });
  const documentQuery = useQuery({
    queryKey: ['dashboard', 'documents'],
    queryFn: dashboardApi.documents,
    refetchInterval: 60_000,
  });

  const isLoading = overviewQuery.isLoading || workflowQuery.isLoading || approvalQuery.isLoading || documentQuery.isLoading;
  const firstError = overviewQuery.error ?? workflowQuery.error ?? approvalQuery.error ?? documentQuery.error;
  const workflowCounts = overviewQuery.data?.workflow_status_counts;
  const activeWorkflows = workflowCounts
    ? ACTIVE_STATUSES.reduce((total, status) => total + (workflowCounts[status] ?? 0), 0)
    : null;
  const runningTaskCount = overviewQuery.data?.task_status_counts['running'] ?? null;
  const pendingApprovals = approvalQuery.data
    ? approvalQuery.data.filter((approval) => approval.status === 'pending').length
    : null;
  const knowledgeDocuments = documentQuery.data?.length ?? null;

  const refresh = () => {
    void Promise.all([
      overviewQuery.refetch(),
      workflowQuery.refetch(),
      approvalQuery.refetch(),
      documentQuery.refetch(),
    ]);
  };

  return (
    <section className="phase2-page phase2-dashboard-page">
      <div className="phase2-dashboard-welcome">
        <div>
          <span className="phase2-kicker">OPERATIONS CENTER</span>
          <h1>Welcome to AgentOps-OS</h1>
          <p>Build, run and monitor AI agents for real business workflows.</p>
        </div>
        <div className="phase2-heading-actions">
          <Button variant="secondary" size="sm" onClick={refresh} disabled={isLoading}>
            <RefreshCw size={15} /> Refresh
          </Button>
          <Link to="/app/workflows/new" className="phase2-primary-link"><Plus size={16} /> New Workflow</Link>
        </div>
      </div>

      {firstError && (
        <div className="phase2-alert error">
          {getApiErrorMessage(firstError, 'One or more dashboard APIs could not be loaded. Check backend availability and permissions.')}
        </div>
      )}

      {isLoading ? (
        <div className="phase2-loading">Loading workspace metrics…</div>
      ) : (
        <>
          <StatisticsCards
            activeWorkflows={overviewQuery.isError ? null : activeWorkflows}
            runningAgentCount={null}
            runningTaskCount={overviewQuery.isError ? null : runningTaskCount}
            pendingApprovals={approvalQuery.isError ? null : pendingApprovals}
            knowledgeDocuments={documentQuery.isError ? null : knowledgeDocuments}
          />

          <div className="phase2-dashboard-grid">
            <WorkflowChart workflows={workflowQuery.data?.items ?? []} isUnavailable={workflowQuery.isError} />
            <RecentActivity
              workflows={workflowQuery.data?.items ?? []}
              approvals={approvalQuery.data ?? []}
              documents={documentQuery.data ?? []}
            />
          </div>

          <section className="phase2-quick-actions">
            <div className="phase2-quick-intro">
              <span className="phase2-kicker">GET STARTED</span>
              <h2>Quick actions</h2>
              <p>Move from workflow design to execution monitoring.</p>
            </div>
            <Link to="/app/workflows/new" className="phase2-action-card">
              <span><Plus size={17} /></span><strong>Create a workflow</strong>
              <small>Design a dependency-aware task graph.</small><ArrowRight size={15} />
            </Link>
            <Link to="/app/workflows" className="phase2-action-card">
              <span><RefreshCw size={17} /></span><strong>Review executions</strong>
              <small>Inspect recent runs and task outcomes.</small><ArrowRight size={15} />
            </Link>
            <Link to="/app/approvals" className="phase2-action-card">
              <span><ArrowRight size={17} /></span><strong>Approval inbox</strong>
              <small>Review protected actions awaiting a decision.</small><ArrowRight size={15} />
            </Link>
          </section>

          <p className="phase2-data-note">
            Metrics are loaded from the authenticated observability, approvals and knowledge APIs. The backend exposes running task steps, but not a live running-agent inventory; that card is intentionally shown as unavailable rather than presenting task count as agent count.
          </p>
        </>
      )}
    </section>
  );
}
