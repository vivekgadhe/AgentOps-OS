import { describe, expect, it } from 'vitest';
import type { Edge } from '@xyflow/react';
import { validateAndBuildTasks, type BuilderNode } from './workflow-utils';

const node = (id: string, label: string, toolName = 'summarize_input', kind: BuilderNode['data']['kind'] = 'tool'): BuilderNode => ({
  id,
  type: 'workflow',
  position: { x: 0, y: 0 },
  data: { label, kind, toolName, inputJson: '{"text":"hello"}', maxAttempts: 3, timeoutSeconds: 300 },
});

describe('validateAndBuildTasks', () => {
  it('converts directed edges into dependency keys', () => {
    const nodes = [node('node-a', 'First'), node('node-b', 'Second')];
    const edges: Edge[] = [{ id: 'ab', source: 'node-a', target: 'node-b' }];
    const result = validateAndBuildTasks(nodes, edges);
    expect(result.errors).toEqual([]);
    expect(result.tasks).toHaveLength(2);
    expect(result.tasks[1]?.depends_on).toEqual([result.tasks[0]?.key]);
    expect(result.tasks[1]?.input_data).toEqual({ text: 'hello' });
  });

  it('keeps Start and End as visual markers and excludes them from backend tasks', () => {
    const nodes = [
      node('start', 'Start', '', 'start'),
      node('agent', 'Planning Agent', 'summarize_input', 'agent'),
      node('tool', 'Analysis Agent', 'text_statistics', 'agent'),
      node('end', 'End', '', 'end'),
    ];
    const edges: Edge[] = [
      { id: 'sa', source: 'start', target: 'agent' },
      { id: 'at', source: 'agent', target: 'tool' },
      { id: 'te', source: 'tool', target: 'end' },
    ];
    const result = validateAndBuildTasks(nodes, edges);
    expect(result.errors).toEqual([]);
    expect(result.tasks).toHaveLength(2);
    expect(result.tasks[1]?.depends_on).toEqual([result.tasks[0]?.key]);
  });


  it('preserves fan-out and join dependencies for the reference workflow layout', () => {
    const nodes = [
      node('planning', 'Planning Agent', 'summarize_input', 'agent'),
      node('analysis', 'Analysis Agent', 'text_statistics', 'agent'),
      node('approval', 'Human Approval', 'approval_required_tool', 'approval'),
      node('report', 'Report', 'normalize_whitespace', 'tool'),
      node('action', 'Action Agent', 'execute_action', 'agent'),
      node('generate', 'Generate Report', 'normalize_whitespace', 'tool'),
    ];
    const edges: Edge[] = [
      { id: 'planning-analysis', source: 'planning', target: 'analysis' },
      { id: 'analysis-approval', source: 'analysis', target: 'approval' },
      { id: 'analysis-report', source: 'analysis', target: 'report' },
      { id: 'approval-action', source: 'approval', target: 'action' },
      { id: 'action-generate', source: 'action', target: 'generate' },
      { id: 'report-generate', source: 'report', target: 'generate' },
    ];
    const result = validateAndBuildTasks(nodes, edges);
    const byName = new Map(result.tasks.map((task) => [task.name, task]));
    expect(result.errors).toEqual([]);
    expect(byName.get('Analysis Agent')?.depends_on).toEqual([byName.get('Planning Agent')?.key]);
    expect(byName.get('Action Agent')?.depends_on).toEqual([byName.get('Human Approval')?.key]);
    expect(byName.get('Generate Report')?.depends_on).toEqual([
      byName.get('Action Agent')?.key,
      byName.get('Report')?.key,
    ]);
  });

  it('rejects cyclic dependencies', () => {
    const nodes = [node('node-a', 'First'), node('node-b', 'Second')];
    const edges: Edge[] = [
      { id: 'ab', source: 'node-a', target: 'node-b' },
      { id: 'ba', source: 'node-b', target: 'node-a' },
    ];
    expect(validateAndBuildTasks(nodes, edges).errors.join(' ')).toContain('cycle');
  });

  it('blocks conditional, delay and loop placeholders from execution', () => {
    const condition = node('condition-1', 'Condition', '', 'condition');
    const delay = node('delay-1', 'Delay', '', 'delay');
    const loop = node('loop-1', 'Loop', '', 'loop');
    const result = validateAndBuildTasks([node('task-1', 'Task'), condition, delay, loop], []);
    expect(result.errors.join(' ')).toContain('not supported');
  });

  it('rejects malformed JSON input', () => {
    const item = { ...node('node-a', 'First'), data: { ...node('node-a', 'First').data, inputJson: '{' } };
    expect(validateAndBuildTasks([item], []).errors.join(' ')).toContain('valid JSON');
  });

  it('rejects incoming edges to Start and outgoing edges from End', () => {
    const start = node('start', 'Start', '', 'start');
    const end = node('end', 'End', '', 'end');
    const task = node('task', 'Task');
    const result = validateAndBuildTasks([start, end, task], [
      { id: 'bad-one', source: 'task', target: 'start' },
      { id: 'bad-two', source: 'end', target: 'task' },
    ]);
    expect(result.errors.join(' ')).toContain('Start marker');
    expect(result.errors.join(' ')).toContain('End marker');
  });
});
