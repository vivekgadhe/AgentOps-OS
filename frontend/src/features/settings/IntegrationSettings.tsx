import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Cpu, PlugZap, Save, ShieldCheck, Trash2, Wifi } from "lucide-react";

import { useAuth } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../../lib/api-error";
import { settingsService, type AIProviderName, type AIProviderUpsertPayload } from "../../services/settings.service";

const providerInfo: { name: AIProviderName; title: string; description: string; defaultModel: string; defaultUrl: string }[] = [
  { name: "ollama", title: "Ollama", description: "Local model runtime. API keys are not used for this provider.", defaultModel: "qwen3.5:0.8b", defaultUrl: "http://localhost:11434" },
  { name: "openai", title: "OpenAI", description: "Hosted OpenAI models. The API key is encrypted by the backend.", defaultModel: "", defaultUrl: "" },
  { name: "groq", title: "Groq", description: "Hosted Groq models. The API key is encrypted by the backend.", defaultModel: "", defaultUrl: "" },
];

export function IntegrationSettings() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const canManage = user?.role === "admin" || user?.role === "operator";
  const providersQuery = useQuery({ queryKey: ["settings", "providers"], queryFn: settingsService.getProviders });
  const [editing, setEditing] = useState<AIProviderName | null>(null);
  const [modelName, setModelName] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("http://localhost:11434");
  const [priority, setPriority] = useState(0);
  const [enabled, setEnabled] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const saveMutation = useMutation({
    mutationFn: ({ provider, payload }: { provider: AIProviderName; payload: AIProviderUpsertPayload }) => settingsService.saveProvider(provider, payload),
    onSuccess: async (result) => {
      setNotice(`${result.provider} configuration saved. Secrets are never returned by the API.`);
      setEditing(null);
      setApiKey("");
      await queryClient.invalidateQueries({ queryKey: ["settings", "providers"] });
    },
    onError: (error: unknown) => setFormError(getApiErrorMessage(error, "Unable to save provider configuration.")),
  });
  const deleteMutation = useMutation({
    mutationFn: (provider: AIProviderName) => settingsService.deleteProvider(provider),
    onSuccess: async () => { setNotice("Provider configuration deleted."); await queryClient.invalidateQueries({ queryKey: ["settings", "providers"] }); },
    onError: (error: unknown) => setFormError(getApiErrorMessage(error, "Unable to delete provider configuration.")),
  });
  const testMutation = useMutation({
    mutationFn: settingsService.testProviderChain,
    onSuccess: (result) => setNotice(`${result.success ? "Provider test succeeded" : "Provider test did not succeed"}: ${result.provider} · ${result.model_name}. ${result.message}`),
    onError: (error: unknown) => setFormError(getApiErrorMessage(error, "Provider health check failed.")),
  });

  function openEditor(provider: AIProviderName) {
    const current = providersQuery.data?.find((item) => item.provider === provider);
    const info = providerInfo.find((item) => item.name === provider);
    setEditing(provider);
    setModelName(current?.model_name ?? info?.defaultModel ?? "");
    setApiKey("");
    setBaseUrl(current?.base_url ?? info?.defaultUrl ?? "");
    setPriority(current?.priority ?? 0);
    setEnabled(current?.enabled ?? true);
    setFormError(null);
    setNotice(null);
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editing) return;
    setFormError(null);
    const existing = providersQuery.data?.find((item) => item.provider === editing);
    if (editing !== "ollama" && !existing?.api_key_configured && !apiKey.trim()) {
      setFormError("An API key is required when configuring OpenAI or Groq for the first time.");
      return;
    }
    const payload: AIProviderUpsertPayload = {
      model_name: modelName.trim(),
      priority,
      enabled,
      ...(editing === "ollama" ? { base_url: baseUrl.trim() || null } : {}),
      ...(apiKey.trim() ? { api_key: apiKey.trim() } : {}),
    };
    saveMutation.mutate({ provider: editing, payload });
  }

  return (
    <div className="p4-settings-stack">
      <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">AI PROVIDER ROUTING</span><h2>Model integrations</h2><p>Per-account provider configuration from the existing encrypted provider API.</p></div><PlugZap size={22} /></div>
        {providersQuery.isPending ? <div className="p4-empty p4-empty-compact">Loading provider configuration…</div> : providersQuery.isError ? <div className="p4-error-banner">{getApiErrorMessage(providersQuery.error, "Unable to load providers.")}</div> : (
          <div className="p4-provider-grid">{providerInfo.map((provider) => {
            const current = providersQuery.data?.find((item) => item.provider === provider.name);
            return <article className="p4-provider-card" key={provider.name}><div className="p4-provider-card-top"><span className="p4-provider-icon"><Cpu size={18} /></span><span className={`p4-status-chip ${current?.enabled ? "is-enabled" : "is-readonly"}`}>{current ? (current.enabled ? "Enabled" : "Disabled") : "Not configured"}</span></div><h3>{provider.title}</h3><p>{provider.description}</p>
              {current ? <div className="p4-provider-meta"><span>Model <strong>{current.model_name}</strong></span><span>Priority <strong>{current.priority}</strong></span>{provider.name !== "ollama" && <span>API key <strong>{current.api_key_configured ? "Configured · hidden" : "Not configured"}</strong></span>}{provider.name === "ollama" && <span>Base URL <strong>{current.base_url || "Backend default"}</strong></span>}</div> : <div className="p4-provider-meta"><span>Default integration is not configured for this account.</span></div>}
              <div className="p4-provider-actions"><button className="p4-primary-button" type="button" disabled={!canManage} onClick={() => openEditor(provider.name)}>{current ? "Edit configuration" : "Configure provider"}</button>{current && <button className="p4-icon-button is-danger" type="button" disabled={!canManage || deleteMutation.isPending} aria-label={`Delete ${provider.title} configuration`} onClick={() => { if (window.confirm(`Delete ${provider.title} provider configuration?`)) deleteMutation.mutate(provider.name); }}><Trash2 size={15} /></button>}</div>
            </article>;
          })}</div>
        )}
        {!canManage && <p className="p4-chart-note">Your current role can view provider settings but cannot change them. The API permits provider writes for admin and operator roles.</p>}
      </section>

      {editing && <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">PROVIDER CONFIGURATION</span><h2>Configure {providerInfo.find((item) => item.name === editing)?.title}</h2><p>Credentials are sent only to the authenticated provider API and are not displayed after saving.</p></div><button className="p4-secondary-button" type="button" onClick={() => setEditing(null)}>Close</button></div>
        <form className="p4-form p4-provider-form" onSubmit={submit}>
          <label>Model name<input required maxLength={120} value={modelName} onChange={(event) => setModelName(event.target.value)} placeholder={editing === "ollama" ? "qwen3.5:0.8b" : "Enter provider model identifier"} /></label>
          {editing === "ollama" ? <label>Ollama base URL<input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="http://localhost:11434" /><small>Backend accepts localhost, 127.0.0.1, ::1 or host.docker.internal.</small></label> : <label>API key<input type="password" autoComplete="new-password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder={providersQuery.data?.some((item) => item.provider === editing && item.api_key_configured) ? "Leave blank to keep the current key" : "Enter API key"} /><small>Existing keys cannot be retrieved. Leave blank to retain the currently encrypted key.</small></label>}
          <div className="p4-form-row"><label>Fallback priority<input type="number" min={0} max={100} value={priority} onChange={(event) => setPriority(Number(event.target.value))} /></label><label className="p4-checkbox-label"><input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} /> Enable provider</label></div>
          {formError && <div className="p4-error-banner" role="alert">{formError}</div>}
          <button className="p4-primary-button" type="submit" disabled={saveMutation.isPending || !modelName.trim()}><Save size={14} />{saveMutation.isPending ? "Saving…" : "Save provider"}</button>
        </form>
      </section>}

      <section className="p4-card p4-provider-test"><div><span className="p4-kicker">CONNECTION CHECK</span><h2>Test configured fallback chain</h2><p>The backend tests whichever enabled provider it selects from the configured priority chain.</p></div><button className="p4-secondary-button" type="button" disabled={!canManage || testMutation.isPending} onClick={() => { setFormError(null); setNotice(null); testMutation.mutate(); }}><Wifi size={14} />{testMutation.isPending ? "Testing…" : "Test providers"}</button></section>
      {formError && !editing && <div className="p4-error-banner" role="alert">{formError}</div>}
      {notice && <div className="p4-success-banner" role="status"><CheckCircle2 size={16} />{notice}</div>}
      <div className="p4-capability-note"><ShieldCheck size={17} /><span>OpenAI and Groq API keys are encrypted by the backend. Ollama is configured with a local base URL and does not require a hosted API key. No key or provider secret is read back to the browser.</span></div>
    </div>
  );
}
