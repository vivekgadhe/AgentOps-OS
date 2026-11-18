import type { Edge, Node } from '@xyflow/react';
import type { WorkflowResponse } from '../dashboard/dashboard.types';

export type WorkflowNodeKind = 'start' | 'end' | 'agent' | 'tool' | 'approval' | 'condition' | 'delay' | 'loop';
export interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  kind: WorkflowNodeKind;
  toolName: string;
  inputJson: string;
  maxAttempts: number;
  timeoutSeconds: number;
}
export type BuilderNode = Node<WorkflowNodeData, 'workflow'>;

export interface WorkflowTaskPayload {
  key: string;
  name: string;
  tool_name: string;
  input_data: Record<string, unknown>;
  max_attempts: number;
  timeout_seconds: number;
  depends_on: string[];
}

export interface ValidationResult {
  errors: string[];
  tasks: WorkflowTaskPayload[];
}

const SAFE_KEY = /^[a-z][a-z0-9_]{0,63}$/;
const BUILT_IN_TOOLS = new Set(['summarize_input', 'text_statistics', 'normalize_whitespace', 'find_matching_lines']);
const NON_EXECUTABLE_KINDS = new Set<WorkflowNodeKind>(['start', 'end', 'condition', 'delay', 'loop']);
const UNSUPPORTED_KINDS = new Set<WorkflowNodeKind>(['condition', 'delay', 'loop']);

function nodeKey(id: string): string {
  const suffix = id.replace(/[^a-zA-Z0-9]/g, '').toLowerCase().slice(-12) || 'step';
  const candidate = `step_${suffix}`.slice(0, 64);
  return SAFE_KEY.test(candidate) ? candidate : 'step_task';
}

export function validateAndBuildTasks(nodes: BuilderNode[], edges: Edge[]): ValidationResult {
  const errors: string[] = [];
  const executable = nodes.filter((node) => !NON_EXECUTABLE_KINDS.has(node.data.kind));
  const unsupported = nodes.filter((node) => UNSUPPORTED_KINDS.has(node.data.kind));
  if (executable.length === 0) errors.push('Add at least one Agent, Tool or Approval task. Start and End are canvas markers only.');
  if (unsupported.length) {
    const labels = [...new Set(unsupported.map((node) => node.data.kind))].join(', ');
    errors.push(`${labels} node execution is not supported by the current backend. Remove these design-only nodes before saving or running this workflow.`);
  }
  if (executable.length > 100) errors.push('The backend accepts no more than 100 task nodes per workflow.');

  const ids = new Set(nodes.map((node) => node.id));
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const graph = new Map(nodes.map((node) => [node.id, [] as string[]]));
  const edgeKeys = new Set<string>();
  for (const edge of edges) {
    if (!ids.has(edge.source) || !ids.has(edge.target)) {
      errors.push('A connection references a node that no longer exists.');
      continue;
    }
    if (edge.source === edge.target) errors.push('A task cannot depend on itself.');
    const source = nodeById.get(edge.source);
    const target = nodeById.get(edge.target);
    if (source?.data.kind === 'end') errors.push('The End marker cannot have outgoing connections.');
    if (target?.data.kind === 'start') errors.push('The Start marker cannot have incoming connections.');
    const pair = `${edge.source}->${edge.target}`;
    if (edgeKeys.has(pair)) errors.push('Duplicate connections are not allowed.');
    edgeKeys.add(pair);
    graph.get(edge.source)?.push(edge.target);
  }

  const visiting = new Set<string>();
  const visited = new Set<string>();
  const visit = (id: string): boolean => {
    if (visiting.has(id)) return false;
    if (visited.has(id)) return true;
    visiting.add(id);
    for (const next of graph.get(id) ?? []) if (!visit(next)) return false;
    visiting.delete(id);
    visited.add(id);
    return true;
  };
  for (const id of ids) {
    if (!visit(id)) {
      errors.push('The workflow contains a cycle. Connections must form a directed acyclic graph.');
      break;
    }
  }

  const keys = new Map(executable.map((node) => [node.id, nodeKey(node.id)]));
  const usedKeys = new Set<string>();
  const tasks: WorkflowTaskPayload[] = [];
  for (const node of executable) {
    const { label, toolName, inputJson, maxAttempts, timeoutSeconds } = node.data;
    if (!label.trim()) errors.push(`Node ${node.id}: task name cannot be blank.`);
    if (!toolName.trim()) errors.push(`Node “${label || node.id}”: enter a registered backend tool name.`);
    if (toolName.trim() && !/^[a-z][a-z0-9_]{0,99}$/.test(toolName.trim())) {
      errors.push(`Node “${label}”: tool names must use lowercase letters, numbers and underscores.`);
    }
    let inputData: Record<string, unknown> = {};
    try {
      const parsed: unknown = JSON.parse(inputJson || '{}');
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) throw new Error('Input must be a JSON object.');
      inputData = parsed as Record<string, unknown>;
    } catch {
      errors.push(`Node “${label || node.id}”: input must be a valid JSON object.`);
    }
    if (!Number.isInteger(maxAttempts) || maxAttempts < 1 || maxAttempts > 10) errors.push(`Node “${label}”: attempts must be between 1 and 10.`);
    if (!Number.isInteger(timeoutSeconds) || timeoutSeconds < 1 || timeoutSeconds > 3600) errors.push(`Node “${label}”: timeout must be between 1 and 3600 seconds.`);

    const key = keys.get(node.id) ?? nodeKey(node.id);
    if (usedKeys.has(key)) errors.push(`Task key collision detected for “${label}”. Recreate the node to generate a unique identifier.`);
    usedKeys.add(key);
    const dependencies = edges
      .filter((edge) => edge.target === node.id)
      .map((edge) => nodeById.get(edge.source))
      .filter((source): source is BuilderNode => source !== undefined && !NON_EXECUTABLE_KINDS.has(source.data.kind))
      .map((source) => keys.get(source.id))
      .filter((value): value is string => Boolean(value));

    tasks.push({
      key,
      name: label.trim(),
      tool_name: toolName.trim(),
      input_data: inputData,
      max_attempts: maxAttempts,
      timeout_seconds: timeoutSeconds,
      depends_on: [...new Set(dependencies)],
    });
  }

  return { errors: [...new Set(errors)], tasks };
}

export function createWorkflowPayload(goal: string, tasks: WorkflowTaskPayload[]) {
  return { goal: goal.trim(), tasks };
}

export function taskProgress(workflow: WorkflowResponse): number {
  if (!workflow.tasks.length) return 0;
  const completed = workflow.tasks.filter((task) => ['succeeded', 'failed', 'skipped', 'cancelled'].includes(task.status)).length;
  return Math.round((completed / workflow.tasks.length) * 100);
}

export const BUILT_IN_TOOL_NAMES = [...BUILT_IN_TOOLS];
