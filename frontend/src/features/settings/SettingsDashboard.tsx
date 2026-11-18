import { useState } from "react";
import { Bell, Bot, Building2, PlugZap, ShieldCheck, Users, Wrench } from "lucide-react";
import { useAuth } from "../auth/AuthProvider";
import { GeneralSettings } from "./GeneralSettings";
import { UserSettings } from "./UserSettings";
import { AgentSettings } from "./AgentSettings";
import { ToolSettings } from "./ToolSettings";
import { IntegrationSettings } from "./IntegrationSettings";
import { SecuritySettings } from "./SecuritySettings";

type SettingsTab = "general" | "users" | "agents" | "tools" | "integrations" | "security";
const tabs: { id: SettingsTab; label: string; icon: typeof Building2 }[] = [
  { id: "general", label: "General", icon: Building2 },
  { id: "users", label: "Users", icon: Users },
  { id: "agents", label: "Agents", icon: Bot },
  { id: "tools", label: "Tools", icon: Wrench },
  { id: "integrations", label: "Integrations", icon: PlugZap },
  { id: "security", label: "Security", icon: ShieldCheck },
];

export function SettingsDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");
  const active = tabs.find((tab) => tab.id === activeTab) ?? tabs[0]!;
  return (
    <main className="p4-page">
      <header className="p4-page-heading"><div><span className="p4-kicker">WORKSPACE ADMINISTRATION</span><h1>Settings</h1><p>Manage account, model integrations and backend-enforced security capabilities.</p></div><div className="p4-settings-account"><span>{user?.email.slice(0, 1).toUpperCase() ?? "U"}</span><div><strong>{user?.email ?? "Current account"}</strong><small>{user?.role ?? "member"}</small></div></div></header>
      <nav className="p4-settings-tabs" aria-label="Settings sections">{tabs.map(({ id, label, icon: Icon }) => <button key={id} type="button" className={activeTab === id ? "is-active" : ""} onClick={() => setActiveTab(id)}><Icon size={15} />{label}</button>)}</nav>
      <div className="p4-settings-tab-heading"><div><span className="p4-kicker">{active.label.toUpperCase()}</span><h2>{active.label} settings</h2></div><span className="p4-readonly-note"><Bell size={13} />API-backed controls only</span></div>
      {activeTab === "general" && <GeneralSettings user={user} />}
      {activeTab === "users" && <UserSettings />}
      {activeTab === "agents" && <AgentSettings />}
      {activeTab === "tools" && <ToolSettings />}
      {activeTab === "integrations" && <IntegrationSettings />}
      {activeTab === "security" && <SecuritySettings />}
      <p className="p4-footnote">The current backend does not provide workspace-wide preference persistence, user-directory/role-edit APIs, agent/tool mutation APIs, or editable approval-policy APIs. Unsupported controls are intentionally read-only rather than simulated.</p>
    </main>
  );
}
