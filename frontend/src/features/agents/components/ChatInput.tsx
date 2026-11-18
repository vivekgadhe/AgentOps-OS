import { ArrowUp, Paperclip } from "lucide-react";
import { useState, type FormEvent } from "react";

interface ChatInputProps {
  disabled?: boolean;
  busy: boolean;
  onSend: (message: string) => Promise<void>;
}

export function ChatInput({ disabled = false, busy, onSend }: ChatInputProps) {
  const [value, setValue] = useState("");
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const prompt = value.trim();
    if (!prompt || disabled || busy) return;
    setValue("");
    await onSend(prompt);
  };

  return (
    <form className="p3-chat-composer" onSubmit={(event) => void submit(event)}>
      <textarea value={value} onChange={(event) => setValue(event.target.value)} rows={2} maxLength={10_000} disabled={disabled || busy} placeholder={disabled ? "Upload a knowledge document to start…" : "Ask a question about your knowledge base…"} aria-label="Message the selected agent" />
      <div className="p3-composer-footer"><span><Paperclip size={13} /> Answers are grounded in your indexed documents</span><button type="submit" className="p3-primary-button" disabled={disabled || busy || !value.trim()}>{busy ? <span className="p3-spinner" /> : <ArrowUp size={16} />}{busy ? "Working…" : "Send"}</button></div>
    </form>
  );
}
