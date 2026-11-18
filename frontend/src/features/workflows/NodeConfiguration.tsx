import { Trash2 } from 'lucide-react';

import type { BuilderNode, WorkflowNodeData } from './workflow-utils';

const TOOL_HINTS = 'Built-ins: summarize_input, text_statistics, normalize_whitespace, find_matching_lines. Trusted server extensions may register additional tools.';

export function NodeConfiguration({
  node,
  onChange,
  onDelete,
}: {
  node: BuilderNode | null;
  onChange: (data: WorkflowNodeData) => void;
  onDelete: () => void;
}) {
  if (!node) {
    return <aside className="workflow-config"><div className="phase2-kicker">STEP CONFIGURATION</div><h3>Node settings</h3><p className="phase2-muted">Select a step on the canvas to configure its task name, backend tool and input.</p></aside>;
  }
  const data = node.data;
  const update = (patch: Partial<WorkflowNodeData>) => onChange({ ...data, ...patch });
  const marker = data.kind === 'start' || data.kind === 'end';
  const unsupported = data.kind === 'condition' || data.kind === 'delay' || data.kind === 'loop';

  return (
    <aside className="workflow-config">
      <div className="phase2-config-top">
        <div><div className="phase2-kicker">STEP CONFIGURATION</div><h3>{marker ? `${data.label} marker` : `${data.kind.charAt(0).toUpperCase()}${data.kind.slice(1)} step`}</h3></div>
        {!marker && <button className="phase2-icon-button danger" type="button" onClick={onDelete} aria-label="Delete selected node"><Trash2 size={16} /></button>}
      </div>
      {marker ? (
        <div className="phase2-node-info"><strong>{data.kind === 'start' ? 'Workflow entry point' : 'Workflow completion point'}</strong><p>This is a canvas-only marker. It is not sent as a task to the backend.</p></div>
      ) : <>
        {unsupported && <div className="phase2-alert warning">This node can be arranged on the canvas for design discussion, but the current backend cannot execute it. Remove it before saving or running.</div>}
        {data.kind === 'approval' && <div className="phase2-alert info">An approval request is created only when the selected server-registered tool has <code>requires_approval=True</code>. This security policy is controlled by backend code, not by this form.</div>}
        {data.kind === 'agent' && <div className="phase2-alert info">The current workflow API executes a registered tool for each task. This is an Agent-labelled task step, not a separate selectable autonomous-agent runtime.</div>}
        <label className="phase2-field">Name<input value={data.label} maxLength={200} onChange={(event) => update({ label: event.target.value })} /></label>
        <label className="phase2-field">{data.kind === 'agent' ? 'Agent execution tool' : 'Backend tool name'}
          <input list="agentops-tool-hints" value={data.toolName} maxLength={100} placeholder="e.g. summarize_input" onChange={(event) => update({ toolName: event.target.value })} />
          <datalist id="agentops-tool-hints"><option value="summarize_input" /><option value="text_statistics" /><option value="normalize_whitespace" /><option value="find_matching_lines" /></datalist>
          <small>{TOOL_HINTS}</small>
        </label>
        <label className="phase2-field">Description / task input (JSON)<textarea rows={8} spellCheck={false} value={data.inputJson} onChange={(event) => update({ inputJson: event.target.value })} /></label>
        <div className="phase2-field-grid">
          <label className="phase2-field">Max attempts<input type="number" min={1} max={10} value={data.maxAttempts} onChange={(event) => update({ maxAttempts: Number(event.target.value) })} /></label>
          <label className="phase2-field">Timeout (seconds)<input type="number" min={1} max={3600} value={data.timeoutSeconds} onChange={(event) => update({ timeoutSeconds: Number(event.target.value) })} /></label>
        </div>
        <div className="workflow-config-footnote">API fields: key, name, tool_name, input_data, max_attempts, timeout_seconds and depends_on.</div>
      </>}
    </aside>
  );
}
