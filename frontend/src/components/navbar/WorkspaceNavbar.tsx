import { useState, type FormEvent } from "react";
import { Search } from "lucide-react";
import { useNavigate } from "react-router-dom";

import type { AuthUser } from "../../features/auth/auth.types";

interface WorkspaceNavbarProps {
  user: AuthUser | null;
  currentLabel: string;
}

export function WorkspaceNavbar({ user, currentLabel }: WorkspaceNavbarProps) {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    navigate(searchTerm.trim() ? `/app/workflows?search=${encodeURIComponent(searchTerm.trim())}` : "/app/workflows");
  };

  return (
    <header className="workspace-topbar">
      <div className="breadcrumb">Workspace<span>/</span>{currentLabel}</div>
      <form className="workspace-topbar-search" onSubmit={submitSearch} role="search">
        <Search size={15} /><input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search workflows and runs…" aria-label="Search workflows and runs" />
      </form>
      <div className="workspace-user"><span className="user-avatar">{user?.email.slice(0, 1).toUpperCase() ?? "U"}</span><span className="user-meta"><strong>{user?.email ?? "Signed-in user"}</strong><small>{user?.role ?? "member"}</small></span></div>
    </header>
  );
}
