import { useCallback, useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { addEdge, ReactFlowProvider, useEdgesState, useNodesState, type Connection, type Edge } from '@xyflow/react';
import { ArrowLeft, LayoutTemplate, Play, Save, ShieldAlert } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

import { Button } from '../../components/ui/Button';
import { getApiErrorMessage } from '../../lib/api-error';
import { workflowApi } from '../dashboard/dashboard.api';
import { NodeConfiguration } from './NodeConfiguration';
import { NodePalette } from './NodePalette';
import { WorkflowCanvas } from './WorkflowCanvas';
import { validateAndBuildTasks, type BuilderNode, type WorkflowNodeData, type WorkflowNodeKind } from './workflow-utils';

const START_NODE: BuilderNode = {
  id: 'workflow-start', type: 'workflow', position: { x: 250, y: 30 }, draggable: false, deletable: false, selectable: false,
  data: { label: 'Start', kind: 'start', toolName: '', inputJson: '{}', maxAttempts: 1, timeoutSeconds: 1 },
};
const END_NODE: BuilderNode = {
  id: 'workflow-end', type: 'workflow', position: { x: 250, y: 560 }, draggable: false, deletable: false, selectable: false,
  data: { label: 'End', kind: 'end', toolName: '', inputJson: '{}', maxAttempts: 1, timeoutSeconds: 1 },
};
const INITIAL_NODES: BuilderNode[] = [START_NODE, END_NODE];
let nodeCounter = 0;

function makeNode(kind: WorkflowNodeKind, position: { x: number; y: number }): BuilderNode {
  nodeCounter += 1;
  const names: Record<WorkflowNodeKind, string> = {
    start: 'Start', end: 'End', agent: 'Analysis Agent', tool: 'Tool Step', approval: 'Human Approval',
    condition: 'Condition', delay: 'Delay', loop: 'Loop',
  };
  const defaultTools: Partial<Record<WorkflowNodeKind, string>> = { agent: 'summarize_input', tool: 'text_statistics' };
  return {
    id: `node_${Date.now()}_${nodeCounter}`,
    type: 'workflow',
    position,
    data: { label: names[kind], kind, toolName: defaultTools[kind] ?? '', inputJson: '{}', maxAttempts: 3, timeoutSeconds: 300 },
  };
}

function createReferenceLayout(): { nodes: BuilderNode[]; edges: Edge[] } {
  const make = (
    id: string,
    kind: WorkflowNodeKind,
    label: string,
    toolName: string,
    inputJson: string,
    position: { x: number; y: number },
  ): BuilderNode => ({
    id,
    type: 'workflow',
    position,
    data: { label, kind, toolName, inputJson, maxAttempts: 3, timeoutSeconds: 300 },
  });

  const nodes: BuilderNode[] = [
    { ...START_NODE, position: { x: 255, y: 12 } },
    make('example-planning', 'agent', 'Planning Agent', 'summarize_input', JSON.stringify({ text: 'Review the incoming business request and outline the key work.' }, null, 2), { x: 255, y: 105 }),
    make('example-analysis', 'agent', 'Analysis Agent', 'text_statistics', JSON.stringify({ text: 'Replace this sample with the business content to analyze.' }, null, 2), { x: 255, y: 215 }),
    make('example-approval', 'approval', 'Human Approval', '', '{}', { x: 35, y: 350 }),
    make('example-report', 'tool', 'Report', 'normalize_whitespace', JSON.stringify({ text: 'Replace this sample with the report content.' }, null, 2), { x: 475, y: 350 }),
    make('example-action', 'agent', 'Action Agent', '', '{}', { x: 35, y: 485 }),
    make('example-generate-report', 'tool', 'Generate Report', 'summarize_input', JSON.stringify({ text: 'Replace this sample with the final report input.' }, null, 2), { x: 255, y: 595 }),
    { ...END_NODE, position: { x: 255, y: 705 } },
  ];

  const edges: Edge[] = [
    { id: 'example-start-planning', source: 'workflow-start', target: 'example-planning' },
    { id: 'example-planning-analysis', source: 'example-planning', target: 'example-analysis' },
    { id: 'example-analysis-approval', source: 'example-analysis', target: 'example-approval' },
    { id: 'example-analysis-report', source: 'example-analysis', target: 'example-report' },
    { id: 'example-approval-action', source: 'example-approval', target: 'example-action' },
    { id: 'example-action-generate', source: 'example-action', target: 'example-generate-report' },
    { id: 'example-report-generate', source: 'example-report', target: 'example-generate-report' },
    { id: 'example-generate-end', source: 'example-generate-report', target: 'workflow-end' },
  ];

  return { nodes, edges };
}

function BuilderInner() {
  const navigate = useNavigate();
  const [goal, setGoal] = useState('');
  const [nodes, setNodes, onNodesChange] = useNodesState<BuilderNode>(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [createdRunId, setCreatedRunId] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [operationError, setOperationError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const selectedNode = useMemo(() => nodes.find((node) => node.id === selectedNodeId) ?? null, [nodes, selectedNodeId]);
  const validation = useMemo(() => validateAndBuildTasks(nodes, edges), [nodes, edges]);

  const invalidateSavedRun = useCallback(() => {
    setCreatedRunId(null);
    setNotice(null);
  }, []);

  const createMutation = useMutation({
    mutationFn: () => workflowApi.create({ goal: goal.trim(), tasks: validation.tasks }),
    onSuccess: (workflow) => {
      setCreatedRunId(workflow.id);
      setNotice('Saved as a workflow run. The current backend does not expose a separate reusable workflow-template API.');
      setOperationError(null);
    },
    onError: (error) => setOperationError(getApiErrorMessage(error, 'Unable to save the workflow.')),
  });

  const executeMutation = useMutation({
    mutationFn: async () => {
      let runId = createdRunId;
      if (!runId) {
        const created = await workflowApi.create({ goal: goal.trim(), tasks: validation.tasks });
        runId = created.id;
        setCreatedRunId(runId);
      }
      return workflowApi.execute(runId);
    },
    onSuccess: (workflow) => navigate(`/app/workflows/${workflow.id}`),
    onError: (error) => setOperationError(getApiErrorMessage(error, 'Unable to start workflow execution.')),
  });

  const addNode = useCallback((kind: WorkflowNodeKind, position?: { x: number; y: number }) => {
    if (['start', 'end'].includes(kind)) return;
    const location = position ?? { x: 90 + (nodes.length % 2) * 245, y: 160 + Math.floor(nodes.length / 2) * 145 };
    const node = makeNode(kind, location);
    setNodes((current) => [...current, node]);
    setSelectedNodeId(node.id);
    invalidateSavedRun();
    setValidationErrors([]);
    setOperationError(null);
  }, [invalidateSavedRun, nodes.length, setNodes]);

  const connect = useCallback((connection: Connection) => {
    setEdges((current) => addEdge({ ...connection, id: `edge_${connection.source}_${connection.target}` }, current));
    invalidateSavedRun();
  }, [invalidateSavedRun, setEdges]);

  const updateSelected = (data: WorkflowNodeData) => {
    if (!selectedNode || ['start', 'end'].includes(selectedNode.data.kind)) return;
    setNodes((current) => current.map((node) => node.id === selectedNode.id ? { ...node, data } : node));
    invalidateSavedRun();
  };

  const removeSelected = () => {
    if (!selectedNode || ['start', 'end'].includes(selectedNode.data.kind)) return;
    setNodes((current) => current.filter((node) => node.id !== selectedNode.id));
    setEdges((current) => current.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id));
    setSelectedNodeId(null);
    invalidateSavedRun();
  };

  const loadReferenceLayout = () => {
    const example = createReferenceLayout();
    setNodes(example.nodes);
    setEdges(example.edges);
    setGoal('Review a business request, prepare an action for human approval, and generate a report.');
    setSelectedNodeId('example-approval');
    setCreatedRunId(null);
    setValidationErrors([]);
    setOperationError(null);
    setNotice('Reference layout loaded. Replace the sample inputs and configure the Approval and Action Agent nodes with tools registered by your backend before saving or running.');
  };

  const validate = (): boolean => {
    const errors = [...validation.errors];
    if (!goal.trim()) errors.unshift('Enter a workflow goal.');
    if (goal.trim().length > 10_000) errors.unshift('Workflow goal must be 10,000 characters or fewer.');
    setValidationErrors(errors);
    setOperationError(null);
    return errors.length === 0;
  };

  const save = () => {
    if (createdRunId) {
      setNotice('This design is already saved as a workflow run. The backend does not support editing an existing run; modify the graph to create a new run.');
      return;
    }
    if (validate()) createMutation.mutate();
  };
  const run = () => { if (validate()) executeMutation.mutate(); };

  return (
    <section className="phase2-page phase2-builder-page">
      <div className="phase2-page-heading">
        <div><Link to="/app/workflows" className="phase2-back-link"><ArrowLeft size={14} /> Workflows</Link><span className="phase2-kicker">VISUAL DESIGNER</span><h1>Workflow Builder</h1><p>Create a visual task graph and preserve backend dependency-aware execution.</p></div>
        <div className="phase2-heading-actions">
          <Button variant="secondary" onClick={loadReferenceLayout}><LayoutTemplate size={16} /> Load reference layout</Button>
          <Button variant="secondary" onClick={save} disabled={createMutation.isPending || Boolean(createdRunId)}><Save size={16} /> {createdRunId ? 'Saved' : 'Save'}</Button>
          <Button onClick={run} disabled={executeMutation.isPending || createMutation.isPending}><Play size={16} /> {executeMutation.isPending ? 'Starting…' : 'Run Workflow'}</Button>
        </div>
      </div>

      <label className="phase2-field workflow-goal-field">Workflow goal<textarea rows={2} maxLength={10_000} value={goal} onChange={(event) => { setGoal(event.target.value); invalidateSavedRun(); }} placeholder="Describe the outcome this workflow should accomplish…" /></label>
      {createdRunId && <div className="phase2-alert success">Workflow run created: <strong>{createdRunId}</strong>. <Link to={`/app/workflows/${createdRunId}`}>Open execution</Link></div>}
      {notice && <div className="phase2-alert info">{notice}</div>}
      {operationError && <div className="phase2-alert error">{operationError}</div>}
      {validationErrors.length > 0 && <div className="phase2-alert error"><strong>Fix these items before saving or running:</strong><ul>{validationErrors.map((error) => <li key={error}>{error}</li>)}</ul></div>}

      <div className="workflow-builder-layout">
        <NodePalette onAdd={addNode} />
        <div className="workflow-canvas-column">
          <div className="workflow-canvas-toolbar"><span>{nodes.filter((node) => !['start', 'end'].includes(node.data.kind)).length} steps · {edges.length} connections</span><span>Drag from palette · Connect handles · Select a step to configure</span></div>
          <WorkflowCanvas nodes={nodes} edges={edges} onNodesChange={(changes) => { onNodesChange(changes); invalidateSavedRun(); }} onEdgesChange={(changes) => { onEdgesChange(changes); invalidateSavedRun(); }} onConnect={connect} onDropNode={addNode} onSelectNode={(node) => setSelectedNodeId(node?.id ?? null)} />
          <div className="workflow-semantics-note"><ShieldAlert size={15} /><span>Connections are saved as prerequisite dependencies. Fan-out runs all eligible downstream tasks after prerequisites succeed. Condition, Delay and Loop are shown as design markers only because the current backend does not implement their execution semantics.</span></div>
        </div>
        <NodeConfiguration node={selectedNode} onChange={updateSelected} onDelete={removeSelected} />
      </div>
    </section>
  );
}

export function WorkflowBuilder() {
  return <ReactFlowProvider><BuilderInner /></ReactFlowProvider>;
}
