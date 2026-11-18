import { Activity, CheckCircle2, Clock3, XCircle } from "lucide-react";

interface AgentExecutionStatusProps {
  agentName: string;
  status: "idle" | "running" | "succeeded" | "failed";
  lastRunAt: string | null;
}

export function AgentExecutionStatus({ agentName, status, lastRunAt }: AgentExecutionStatusProps) {
  const Icon = status === "succeeded" ? CheckCircle2 : status === "failed" ? XCircle : status === "running" ? Activity : Clock3;
  const label = status === "idle" ? "Ready" : status === "running" ? "Generating" : status === "succeeded" ? "Completed" : "Request failed";
  return <div className={`p3-agent-status ${status}`}><Icon size={15} /><span><strong>{agentName}</strong><small>{label}{lastRunAt ? ` · ${new Intl.DateTimeFormat(undefined, { timeStyle: "short" }).format(new Date(lastRunAt))}` : " · No request in this session"}</small></span></div>;
}
