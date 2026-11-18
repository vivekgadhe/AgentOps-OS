import { useState } from "react";
import { Bot, FileText, MessageSquareText, RefreshCw, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../../lib/api-error";
import { agentService } from "../../services/agent.service";
import type { KnowledgeAnswerResponse } from "../../types/knowledge";
import { useKnowledgeDocuments } from "../knowledge/hooks/useKnowledge";
import { AgentExecutionStatus } from "./components/AgentExecutionStatus";
import { ChatInput } from "./components/ChatInput";
import { ChatMessage, type ChatMessageItem } from "./components/ChatMessage";

type AgentChoice = "analysis_agent" | "report_agent";

function makeId(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

export function AgentsPage() {
  const { user } = useAuth();
  const canRunAgents = user?.role === "admin" || user?.role === "operator";
  const [selectedAgent, setSelectedAgent] = useState<AgentChoice>("analysis_agent");
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [lastStatus, setLastStatus] = useState<"idle" | "running" | "succeeded" | "failed">("idle");
  const [lastRunAt, setLastRunAt] = useState<string | null>(null);

  const documentsQuery = useKnowledgeDocuments();
  const documentCount = documentsQuery.data?.length ?? 0;
  const selectedName = selectedAgent === "analysis_agent" ? "Analysis Agent" : "Report Agent";

  const send = async (prompt: string) => {
    setMessages((current) => [...current, { id: makeId(), role: "user", content: prompt }]);
    setBusy(true);
    setLastStatus("running");
    setLastRunAt(new Date().toISOString());
    try {
      const payload = { query: prompt, top_k: 5 };
      const result: KnowledgeAnswerResponse = selectedAgent === "analysis_agent"
        ? await agentService.askAnalysisAgent(payload)
        : await agentService.askReportAgent(payload);
      const responseContent = result.answer.status === "failed"
        ? result.answer.error_message ?? result.answer.summary
        : result.answer.summary;
      setMessages((current) => [...current, {
        id: makeId(),
        role: "assistant",
        content: responseContent,
        agentName: result.answer.agent_name,
        status: result.answer.status,
        citations: result.citations,
        output: result.answer.output,
      }]);
      setLastStatus(result.answer.status);
    } catch (error) {
      const message = getApiErrorMessage(error, "The agent request failed. Check your configured AI provider, Ollama embedding service and knowledge documents.");
      setMessages((current) => [...current, { id: makeId(), role: "assistant", content: message, agentName: selectedAgent, status: "failed" }]);
      setLastStatus("failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="p3-page phase2-page">
      <header className="p3-page-heading">
        <div><span className="p3-eyebrow"><Bot size={13} /> AGENT WORKSPACE</span><h1>Agents & Chat</h1><p>Ask knowledge-grounded agents to analyze your documents or prepare a structured report.</p></div>
        <div className="p3-heading-status"><span className="p3-status-dot" /> Local knowledge context</div>
      </header>

      {!canRunAgents && <div className="p3-warning-banner">Agent queries require an administrator or operator role. You can still review the available agent capabilities.</div>}
      {documentsQuery.isError && <div className="p3-inline-error" role="alert">{getApiErrorMessage(documentsQuery.error, "Unable to check your knowledge library.")}</div>}

      <div className="p3-agent-workspace">
        <aside className="p3-card p3-agent-sidebar">
          <div className="p3-card-heading"><div><span className="p3-eyebrow">AVAILABLE AGENTS</span><h2>Choose an agent</h2></div><span className="p3-icon-tile violet"><Bot size={18} /></span></div>
          <button type="button" className={`p3-agent-choice${selectedAgent === "analysis_agent" ? " is-selected" : ""}`} onClick={() => setSelectedAgent("analysis_agent")}>
            <span className="p3-agent-choice-icon violet"><Sparkles size={18} /></span><span><strong>Analysis Agent</strong><small>Answers questions using retrieved document passages.</small></span><span className="p3-agent-choice-dot" />
          </button>
          <button type="button" className={`p3-agent-choice${selectedAgent === "report_agent" ? " is-selected" : ""}`} onClick={() => setSelectedAgent("report_agent")}>
            <span className="p3-agent-choice-icon cyan"><FileText size={18} /></span><span><strong>Report Agent</strong><small>Creates a structured report grounded in your documents.</small></span><span className="p3-agent-choice-dot" />
          </button>
          <div className="p3-agent-library-status"><FileText size={16} /><span><strong>{documentsQuery.isLoading ? "…" : documentCount} documents available</strong><small>Only documents owned by your account are retrieved.</small></span><Link to="/app/knowledge">Manage</Link></div>
          <AgentExecutionStatus agentName={selectedName} status={lastStatus} lastRunAt={lastRunAt} />
          <div className="p3-agent-capability-note"><strong>Backend capability</strong><p>The API currently exposes the Analysis and Report knowledge agents. Generic agent discovery, persistent chat sessions and streaming chat are not exposed by this backend.</p></div>
        </aside>

        <section className="p3-card p3-chat-panel">
          <div className="p3-chat-header"><div className="p3-chat-header-icon"><Bot size={19} /></div><div><strong>{selectedName}</strong><small>Knowledge-grounded assistant · top 5 retrieved passages</small></div><button type="button" className="p3-icon-button" disabled={messages.length === 0 || busy} onClick={() => { setMessages([]); setLastStatus("idle"); setLastRunAt(null); }} title="Clear this local conversation" aria-label="Clear conversation"><RefreshCw size={15} /></button></div>
          <div className="p3-chat-thread" aria-live="polite">
            {messages.length === 0 ? <div className="p3-chat-welcome"><span className="p3-chat-welcome-icon"><MessageSquareText size={24} /></span><h2>What would you like to explore?</h2><p>Ask about information contained in your uploaded documents. The selected agent will retrieve relevant passages and return an answer with source citations.</p><div className="p3-prompt-suggestions"><button type="button" disabled={!documentCount || !canRunAgents || busy} onClick={() => void send("Summarize the key points across my uploaded documents.")}>Summarize my documents</button><button type="button" disabled={!documentCount || !canRunAgents || busy} onClick={() => void send("Identify the most important findings and supporting evidence.")}>Find key findings</button></div></div> : messages.map((message) => <ChatMessage key={message.id} message={message} />)}
            {busy && <div className="p3-agent-thinking"><span className="p3-spinner dark" />{selectedName} is retrieving context and generating a response…</div>}
          </div>
          {documentCount === 0 && <div className="p3-chat-upload-prompt">Upload and index at least one document before asking a knowledge-grounded agent. <Link to="/app/knowledge">Open Knowledge</Link></div>}
          <ChatInput busy={busy} disabled={!canRunAgents || documentCount === 0 || documentsQuery.isLoading} onSend={send} />
          <div className="p3-chat-disclaimer">Responses depend on the user's indexed documents and configured AI provider. This conversation is held in page state and is not persisted by the backend.</div>
        </section>
      </div>
    </section>
  );
}
