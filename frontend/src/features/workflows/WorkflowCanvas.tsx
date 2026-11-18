import { useCallback, useMemo, type DragEvent as ReactDragEvent } from 'react';
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  useReactFlow,
  type Connection,
  type Edge,
  type IsValidConnection,
  type NodeProps,
  type OnEdgesChange,
  type OnNodesChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Bot, CheckCircle2, Clock3, GitBranch, Hand, Repeat2, Sparkles, Wrench } from 'lucide-react';

import type { BuilderNode, WorkflowNodeKind } from './workflow-utils';

function WorkflowNodeView({ data, selected }: NodeProps<BuilderNode>) {
  const Icon = data.kind === 'start' ? Sparkles
    : data.kind === 'end' ? CheckCircle2
      : data.kind === 'agent' ? Bot
        : data.kind === 'tool' ? Wrench
          : data.kind === 'approval' ? Hand
            : data.kind === 'condition' ? GitBranch
              : data.kind === 'loop' ? Repeat2 : Clock3;
  const marker = data.kind === 'start' || data.kind === 'end';
  const unsupported = data.kind === 'condition' || data.kind === 'delay' || data.kind === 'loop';
  return (
    <div className={`workflow-node-card ${data.kind}${selected ? ' selected' : ''}${unsupported ? ' unsupported' : ''}`}>
      {data.kind !== 'start' && <Handle type="target" position={Position.Top} />}
      <div className="workflow-node-head"><span className="workflow-node-icon"><Icon size={15} /></span><span>{marker ? 'WORKFLOW' : data.kind.toUpperCase()}</span>{unsupported && <span className="workflow-node-tag">DESIGN ONLY</span>}</div>
      <strong>{data.label || 'Untitled task'}</strong>
      <small>{data.kind === 'start' ? 'Workflow entry point' : data.kind === 'end' ? 'Workflow completion point' : data.toolName || (unsupported ? 'Backend support required' : 'Configure a registered backend tool')}</small>
      {data.kind !== 'end' && <Handle type="source" position={Position.Bottom} />}
    </div>
  );
}

const nodeTypes = { workflow: WorkflowNodeView };
const ALLOWED_DROP_KINDS = ['agent', 'tool', 'approval', 'condition', 'delay', 'loop'];

export function WorkflowCanvas({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onDropNode,
  onSelectNode,
}: {
  nodes: BuilderNode[];
  edges: Edge[];
  onNodesChange: OnNodesChange<BuilderNode>;
  onEdgesChange: OnEdgesChange<Edge>;
  onConnect: (connection: Connection) => void;
  onDropNode: (kind: WorkflowNodeKind, position: { x: number; y: number }) => void;
  onSelectNode: (node: BuilderNode | null) => void;
}) {
  const flow = useReactFlow();
  const nodeById = useMemo(() => {
    const lookup = new Map<string, BuilderNode>();
    for (const node of nodes) lookup.set(node.id, node);
    return lookup;
  }, [nodes]);
  const onDragOver = useCallback((event: ReactDragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);
  const onDrop = useCallback((event: ReactDragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const kind = event.dataTransfer.getData('application/reactflow') as WorkflowNodeKind;
    if (!ALLOWED_DROP_KINDS.includes(kind)) return;
    onDropNode(kind, flow.screenToFlowPosition({ x: event.clientX, y: event.clientY }));
  }, [flow, onDropNode]);
  const isValidConnection: IsValidConnection = useCallback((connection) => {
    if (!connection.source || !connection.target || connection.source === connection.target) return false;
    if (nodeById.get(connection.source)?.data.kind === 'end') return false;
    if (nodeById.get(connection.target)?.data.kind === 'start') return false;
    return !edges.some((edge) => edge.source === connection.source && edge.target === connection.target);
  }, [edges, nodeById]);

  return (
    <div className="workflow-canvas" onDragOver={onDragOver} onDrop={onDrop}>
      <div className="workflow-canvas-grid-label">DESIGN CANVAS <span>{nodes.filter((node) => !['start', 'end'].includes(node.data.kind)).length} steps</span></div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_event, node) => onSelectNode(node as BuilderNode)}
        onPaneClick={() => onSelectNode(null)}
        isValidConnection={isValidConnection}
        fitView
        fitViewOptions={{ padding: 0.22 }}
        minZoom={0.25}
        maxZoom={1.6}
        deleteKeyCode={['Backspace', 'Delete']}
        defaultEdgeOptions={{ type: 'smoothstep', animated: true, style: { stroke: '#9299b5', strokeWidth: 1.8 } }}
      >
        <Background color="#e0e5f0" gap={18} size={1} />
        <MiniMap nodeStrokeWidth={3} zoomable pannable />
        <Controls />
      </ReactFlow>
      {nodes.length <= 2 && <div className="workflow-canvas-empty"><span>✦</span><strong>Your workflow starts here</strong><p>Add Agent, Tool or Approval steps, then connect the handles to define the dependency order.</p></div>}
    </div>
  );
}
