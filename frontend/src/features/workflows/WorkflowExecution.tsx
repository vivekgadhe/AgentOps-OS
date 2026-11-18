import { useMutation, useQuery } from '@tanstack/react-query';
import { AlertTriangle, ArrowLeft, CheckCircle2, Circle, Clock3, Play, RefreshCw, ShieldCheck } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

import { Button } from '../../components/ui/Button';
import { getApiErrorMessage } from '../../lib/api-error';
import { useAuth } from '../auth/AuthProvider';
import { approvalsApi, workflowApi } from '../dashboard/dashboard.api';
import { formatDate, formatDuration, titleCase } from '../dashboard/format';
import { ApprovalActions } from '../approvals/ApprovalActions';
import { taskProgress } from './workflow-utils';

function JsonPanel({ title, value }: { title: string; value: Record<string, unknown> | null }) {
  if (!value || Object.keys(value).length === 0) return null;
  return <details className="phase2-json-panel"><summary>{title}</summary><pre>{JSON.stringify(value, null, 2)}</pre></details>;
}

export function WorkflowExecution() {
  const { workflowId = '' } = useParams();
  const { user } = useAuth();
  const workflowQuery = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => workflowApi.get(workflowId),
    enabled: Boolean(workflowId),
    refetchInterval: (query) => ['running', 'planning', 'awaiting_approval'].includes(query.state.data?.status ?? '') ? 2500 : false,
  });
  const approvalQuery = useQuery({
    queryKey: ['approvals'],
    queryFn: approvalsApi.list,
    enabled: Boolean(workflowId),
    refetchInterval: 10_000,
  });
  const executeMutation = useMutation({
    mutationFn: () => workflowApi.execute(workflowId),
    onSuccess: async () => { await workflowQuery.refetch(); },
  });
  const workflow = workflowQuery.data;
  const progress = workflow ? taskProgress(workflow) : 0;
  const linkedApprovals = (approvalQuery.data ?? []).filter((approval) => approval.workflow_run_id === workflowId);
  const pendingApprovals = linkedApprovals.filter((approval) => approval.status === 'pending');
  const succeededCount = workflow?.tasks.filter((task) => task.status === 'succeeded').length ?? 0;
  const failedCount = workflow?.tasks.filter((task) => task.status === 'failed').length ?? 0;
  const runningCount = workflow?.tasks.filter((task) => task.status === 'running').length ?? 0;

  if (workflowQuery.isLoading) return <section className="phase2-page"><div className="phase2-loading">Loading workflow execution…</div></section>;
  if (workflowQuery.isError || !workflow) return <section className="phase2-page"><div className="phase2-alert error">{getApiErrorMessage(workflowQuery.error, 'Workflow could not be found or is not accessible.')}</div><Link className="phase2-back-link" to="/app/workflows"><ArrowLeft size={14} /> Back to workflows</Link></section>;

  return (
    <section className="phase2-page phase2-execution-page">
      <div className="phase2-page-heading">
        <div><Link to="/app/workflows" className="phase2-back-link"><ArrowLeft size={14} /> Workflows</Link><span className="phase2-kicker">EXECUTION MONITOR</span><h1>Workflow Run: {workflow.goal}</h1><p>Started {formatDate(workflow.started_at)} · Run ID {workflow.id}</p></div>
        <div className="phase2-heading-actions"><Button variant="secondary" size="sm" onClick={() => void workflowQuery.refetch()}><RefreshCw size={15} /> Refresh</Button>{workflow.status === 'pending' && <Button disabled={executeMutation.isPending} onClick={() => executeMutation.mutate()}><Play size={15} /> {executeMutation.isPending ? 'Executing…' : 'Run workflow'}</Button>}</div>
      </div>

      <div className="phase2-execution-banner">
        <div className="phase2-execution-banner-title"><span className="phase2-kicker">OVERALL STATUS</span><span className={`phase2-status-badge ${workflow.status}`}>{titleCase(workflow.status)}</span></div>
        <div className="phase2-execution-progress"><div><strong>{progress}%</strong><span>Tasks completed</span></div><div className="phase2-progress-track"><span style={{ width: `${progress}%` }} /></div></div>
        <div className="phase2-execution-metrics"><span><CheckCircle2 size={14} /> {succeededCount} Succeeded</span><span><Circle size={14} /> {runningCount} Running</span><span><AlertTriangle size={14} /> {failedCount} Failed</span><span>{workflow.tasks.length} Total tasks</span></div>
      </div>

      {executeMutation.error && <div className="phase2-alert error">{getApiErrorMessage(executeMutation.error, 'Unable to start workflow execution.')}</div>}
      {workflow.error && <div className="phase2-alert error"><AlertTriangle size={16} /><div><strong>Workflow error</strong><pre>{JSON.stringify(workflow.error, null, 2)}</pre></div></div>}

      <div className="phase2-execution-layout">
        <section className="phase2-panel phase2-task-panel">
          <div className="phase2-panel-heading"><div><span className="phase2-kicker">TASK GRAPH</span><h2>Execution steps</h2><p>Tasks are displayed in the order returned by the backend.</p></div><span className="phase2-period-pill">Dependency-aware</span></div>
          {workflow.tasks.length === 0 ? <p className="phase2-muted">This workflow has no tasks.</p> : <div className="phase2-task-list">{workflow.tasks.map((task, index) => <article className={`phase2-task-card ${task.status}`} key={task.id}>
            <div className={`phase2-task-index ${task.status}`}>{index + 1}</div>
            <div className="phase2-task-main">
              <div className="phase2-task-heading"><strong>{task.name}</strong><span className={`phase2-status-badge ${task.status}`}>{titleCase(task.status)}</span></div>
              <small>{task.tool_name ?? 'No tool name'} · {task.attempt_count}/{task.max_attempts} attempts</small>
              {task.depends_on.length > 0 && <small>Depends on: {task.depends_on.join(', ')}</small>}
              {task.status === 'running' && <div className="phase2-running-pulse">Task is currently running</div>}
              {task.error && <div className="phase2-task-error"><AlertTriangle size={14} /><pre>{JSON.stringify(task.error, null, 2)}</pre></div>}
              <JsonPanel title="View task input" value={task.input_data} />
              <JsonPanel title="View task output" value={task.output_data} />
              <div className="phase2-task-times"><span><Clock3 size={12} /> Started: {formatDate(task.started_at)}</span><span>Finished: {formatDate(task.finished_at)}</span></div>
            </div>
            {task.status === 'succeeded' ? <CheckCircle2 className="phase2-task-result success" size={18} /> : task.status === 'failed' ? <AlertTriangle className="phase2-task-result failed" size={18} /> : <Circle className="phase2-task-result" size={18} />}
          </article>)}</div>}
        </section>

        <aside className="phase2-side-stack">
          <section className="phase2-panel phase2-inline-approval-panel">
            <div className="phase2-panel-heading"><div><span className="phase2-kicker">HUMAN-IN-THE-LOOP</span><h2><ShieldCheck size={17} /> Human approval required</h2></div><span className="phase2-count-pill">{pendingApprovals.length} pending</span></div>
            {approvalQuery.isError && <div className="phase2-alert error">{getApiErrorMessage(approvalQuery.error, 'Unable to load approval requests for this run.')}</div>}
            {pendingApprovals.length === 0 ? (
              <div className="phase2-inline-approval-empty"><ShieldCheck size={22} /><strong>No pending approval</strong><p>Protected-tool requests for this workflow will appear here when the backend requires a human decision.</p></div>
            ) : pendingApprovals.map((approval) => (
              <article className="phase2-inline-approval-card" key={approval.id}>
                <div className="phase2-inline-approval-copy"><strong>{approval.action_summary}</strong><span>{approval.tool_name} · Requested {formatDate(approval.requested_at)}</span></div>
                <div className="phase2-proposed-actions"><strong>Proposed actions</strong><pre>{JSON.stringify(approval.input_snapshot, null, 2)}</pre></div>
                <div className="phase2-inline-approval-meta"><span>Expires {formatDate(approval.expires_at)}</span><span>Requester {approval.requester_user_id.slice(0, 8)}</span></div>
                <ApprovalActions approval={approval} currentUserId={user?.id ?? ''} role={user?.role ?? ''} onComplete={() => { void workflowQuery.refetch(); void approvalQuery.refetch(); }} />
                <Link className="phase2-related-link" to={`/app/approvals/${approval.id}`}>View approval details <span>→</span></Link>
              </article>
            ))}
            {linkedApprovals.filter((approval) => approval.status !== 'pending').map((approval) => <Link key={approval.id} className="phase2-approval-mini" to={`/app/approvals/${approval.id}`}><strong>{approval.action_summary}</strong><span className={`phase2-status-badge ${approval.status}`}>{titleCase(approval.status)}</span></Link>)}
          </section>

          <section className="phase2-panel"><div className="phase2-panel-heading"><div><span className="phase2-kicker">TIMELINE</span><h2>Execution timeline</h2></div></div>
            <div className="phase2-timeline">
              <div><span className="phase2-timeline-dot" /><strong>Workflow created</strong><small>{formatDate(workflow.created_at)}</small></div>
              {workflow.started_at && <div><span className="phase2-timeline-dot" /><strong>Execution started</strong><small>{formatDate(workflow.started_at)}</small></div>}
              {workflow.tasks.filter((task) => task.started_at || task.finished_at).map((task) => <div key={task.id}><span className={`phase2-timeline-dot ${task.status}`} /><strong>{task.name}: {titleCase(task.status)}</strong><small>{formatDate(task.finished_at ?? task.started_at)}</small></div>)}
              {workflow.finished_at && <div><span className="phase2-timeline-dot final" /><strong>Workflow {titleCase(workflow.status)}</strong><small>{formatDate(workflow.finished_at)}</small></div>}
            </div>
            <p className="phase2-chart-footnote">Timeline timestamps are taken from the workflow and task records. The backend does not expose a separate execution-event stream.</p>
          </section>

          <section className="phase2-panel"><div className="phase2-panel-heading"><h2>Run details</h2></div><div className="phase2-detail-lines"><span>Created <strong>{formatDate(workflow.created_at)}</strong></span><span>Updated <strong>{formatDate(workflow.updated_at)}</strong></span><span>Duration <strong>{workflow.started_at && workflow.finished_at ? formatDuration(new Date(workflow.finished_at).getTime() - new Date(workflow.started_at).getTime()) : 'In progress / not started'}</strong></span></div></section>
          <div className="phase2-alert info phase2-control-note"><strong>Execution controls</strong><span>Pause and cancellation controls are not shown because the current backend does not provide pause or cancel endpoints.</span></div>
        </aside>
      </div>
    </section>
  );
}
