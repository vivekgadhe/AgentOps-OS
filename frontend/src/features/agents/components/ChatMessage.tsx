import { Bot, UserRound } from "lucide-react";

import type { KnowledgeCitation } from "../../../types/knowledge";

export interface ChatMessageItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  agentName?: string;
  status?: "succeeded" | "failed";
  citations?: KnowledgeCitation[];
  output?: Record<string, unknown>;
}

export function ChatMessage({ message }: { message: ChatMessageItem }) {
  const isUser = message.role === "user";
  return (
    <article className={`p3-chat-message ${isUser ? "from-user" : "from-agent"}`}>
      <span className={`p3-chat-avatar ${isUser ? "user" : "agent"}`}>{isUser ? <UserRound size={16} /> : <Bot size={17} />}</span>
      <div className="p3-chat-bubble">
        <div className="p3-chat-message-meta"><strong>{isUser ? "You" : message.agentName === "report_agent" ? "Report Agent" : "Analysis Agent"}</strong>{message.status && <span className={`p3-status-pill ${message.status}`}>{message.status}</span>}</div>
        <p>{message.content}</p>
        {message.citations && message.citations.length > 0 && <div className="p3-chat-citations"><strong>Sources</strong>{message.citations.map((citation) => <div className="p3-chat-citation" key={`${citation.document_id}-${citation.chunk_index}`}><span>{citation.source_id}</span><div><strong>{citation.filename}</strong><small>{citation.page_number ? `Page ${citation.page_number}` : `Chunk ${citation.chunk_index + 1}`} · {Math.round(citation.similarity * 100)}% similarity</small></div></div>)}</div>}
        {message.output && Object.keys(message.output).length > 0 && <details className="p3-agent-output"><summary>View structured agent output</summary><pre>{JSON.stringify(message.output, null, 2)}</pre></details>}
      </div>
    </article>
  );
}
