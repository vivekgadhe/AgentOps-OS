import { Bot, Clock3, GitBranch, Hand, Repeat2, Wrench } from 'lucide-react';
import type { WorkflowNodeKind } from './workflow-utils';

const OPTIONS: Array<{ kind: WorkflowNodeKind; label: string; description: string; icon: typeof Bot; className: string; supported: boolean }> = [
  { kind: 'agent', label: 'Agent Step', description: 'A named task using a server-registered tool.', icon: Bot, className: 'agent', supported: true },
  { kind: 'tool', label: 'Tool Step', description: 'Execute a registered backend tool with JSON input.', icon: Wrench, className: 'tool', supported: true },
  { kind: 'condition', label: 'Condition', description: 'Design marker only; conditional routing is not implemented by this backend.', icon: GitBranch, className: 'condition', supported: false },
  { kind: 'approval', label: 'Approval Step', description: 'An approval is created only by a server tool configured to require approval.', icon: Hand, className: 'approval', supported: true },
  { kind: 'delay', label: 'Delay', description: 'Design marker only; delayed execution is not implemented by this backend.', icon: Clock3, className: 'delay', supported: false },
  { kind: 'loop', label: 'Loop', description: 'Design marker only; the backend requires an acyclic dependency graph.', icon: Repeat2, className: 'loop', supported: false },
];

export function NodePalette({ onAdd }: { onAdd: (kind: WorkflowNodeKind) => void }) {
  return (
    <aside className="workflow-palette">
      <div className="phase2-kicker">ADD STEP</div>
      <h3>Build your flow</h3>
      <p>Drag a step onto the canvas or select it to add. Start and End markers are already on the canvas.</p>
      <div className="workflow-palette-options">
        {OPTIONS.map(({ kind, label, description, icon: Icon, className, supported }) => (
          <button
            key={kind}
            className={`workflow-palette-item ${className}`}
            type="button"
            draggable
            onClick={() => onAdd(kind)}
            onDragStart={(event) => {
              event.dataTransfer.setData('application/reactflow', kind);
              event.dataTransfer.effectAllowed = 'move';
            }}
            title={description}
          >
            <span><Icon size={16} /></span>
            <span className="workflow-palette-copy"><strong>{label}</strong><small>{supported ? description : 'Design-only: backend support required'}</small></span>
            <span className="workflow-palette-add">+</span>
          </button>
        ))}
      </div>
      <div className="workflow-palette-note">
        <strong>Execution model</strong>
        <p>Connections become task dependencies. Fan-out makes every dependent branch eligible when its prerequisites succeed. It is not if/else routing.</p>
      </div>
    </aside>
  );
}
