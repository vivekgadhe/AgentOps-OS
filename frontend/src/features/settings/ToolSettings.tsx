import { Info, Wrench } from "lucide-react";

const tools = [
  { name: "summarize_input", description: "Normalizes supplied text and returns a character count.", roles: "admin, operator, viewer" },
  { name: "text_statistics", description: "Calculates word, character and line counts for supplied text.", roles: "admin, operator" },
  { name: "normalize_whitespace", description: "Collapses repeated whitespace into single spaces.", roles: "admin, operator" },
  { name: "find_matching_lines", description: "Finds text lines containing a case-insensitive query.", roles: "admin, operator" },
];

export function ToolSettings() {
  return (
    <section className="p4-card"><div className="p4-section-heading"><div><span className="p4-kicker">SERVER-REGISTERED CAPABILITIES</span><h2>Built-in tools</h2><p>Reference catalog sourced from the backend's built-in tool registry.</p></div><Wrench size={22} /></div>
      <div className="p4-data-table-wrap"><table className="p4-data-table"><thead><tr><th>Tool</th><th>Description</th><th>Role policy</th></tr></thead><tbody>{tools.map((tool) => <tr key={tool.name}><td><code>{tool.name}</code></td><td>{tool.description}</td><td>{tool.roles}</td></tr>)}</tbody></table></div>
      <div className="p4-capability-note"><Info size={17} /><span>The backend does not expose a tool-registry listing or permission-management API. This list reflects built-in source definitions only; trusted extensions may register additional tools. Tool permissions and approval requirements remain server-controlled and cannot be changed from this screen.</span></div>
    </section>
  );
}
