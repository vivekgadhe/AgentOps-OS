import { useState, type FormEvent } from "react";

import {
  MailPlus,
  ShieldCheck,
  Clock,
  CheckCircle2,
  AlertCircle,
  UserPlus,
  Users,
} from "lucide-react";

import { Button } from "../../components/ui/Button";
import { TextInput } from "../../components/ui/TextInput";

import { authApi } from "../auth/auth.api";
import type {
  InvitationCreateResponse,
  UserRole,
} from "../auth/auth.types";

import { useAuth } from "../auth/AuthProvider";
import { getApiErrorMessage } from "../../lib/api-error";

export function InvitationManagement() {
  const { user } = useAuth();

  const [email, setEmail] = useState("");
  const [role, setRole] = useState<UserRole>("operator");

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [errorMessage, setErrorMessage] = useState<string | null>(
    null,
  );

  const [successResult, setSuccessResult] =
    useState<InvitationCreateResponse | null>(null);

  if (user?.role !== "admin") {
    return (
      <section className="workspace-welcome">
        <div className="rounded-2xl border border-red-200 bg-white p-8">
          <div className="flex items-center gap-3 text-red-600">
            <AlertCircle size={22} />
            <h2 className="text-lg font-bold">
              Administrator access required
            </h2>
          </div>

          <p className="mt-3 text-sm text-slate-600">
            Only workspace administrators can invite new users.
          </p>
        </div>
      </section>
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setErrorMessage(null);
    setSuccessResult(null);

    const normalizedEmail = email.trim().toLowerCase();

    if (!normalizedEmail) {
      setErrorMessage("Please enter an email address.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await authApi.createInvitation({
        email: normalizedEmail,
        role,
      });

      setSuccessResult(result);
      setEmail("");
      setRole("operator");
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(
          error,
          "Unable to send the invitation. Please try again.",
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-welcome">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div>
          <div className="welcome-eyebrow">
            <span className="welcome-eyebrow-dot" />
            USER MANAGEMENT
          </div>

          <h1>Invite Team Members</h1>

          <p>
            Invite users to your AgentOps-OS workspace using
            secure email verification.
          </p>
        </div>

        <div className="rounded-xl bg-violet-50 p-3 text-violet-600">
          <Users size={25} />
        </div>
      </div>

      <div className="mt-9 grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">

        {/* Invitation form */}

        <div className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">

          <div className="mb-7 flex items-center gap-3">
            <div className="rounded-xl bg-violet-50 p-3 text-violet-600">
              <UserPlus size={21} />
            </div>

            <div>
              <h2 className="font-bold text-slate-900">
                Create invitation
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Send a secure six-digit verification code.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="grid gap-5">

            <div className="grid gap-2">
              <label
                htmlFor="invitation-email"
                className="text-sm font-semibold text-slate-700"
              >
                Recipient email
              </label>

              <TextInput
                id="invitation-email"
                type="email"
                placeholder="newuser@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                maxLength={320}
                disabled={isSubmitting}
                className="border-slate-200 bg-white text-slate-900 placeholder:text-slate-400"
              />
            </div>

            <div className="grid gap-2">
              <label
                htmlFor="invitation-role"
                className="text-sm font-semibold text-slate-700"
              >
                Assign workspace role
              </label>

              <select
                id="invitation-role"
                value={role}
                onChange={(event) =>
                  setRole(event.target.value as UserRole)
                }
                disabled={isSubmitting}
                className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-800 outline-none focus:border-violet-400 focus:ring-4 focus:ring-violet-500/10"
              >
                <option value="operator">
                  Operator — Execute workflows and use agents
                </option>

                <option value="viewer">
                  Viewer — Read-only access
                </option>

                <option value="admin">
                  Administrator — Manage workspace
                </option>
              </select>

              <p className="text-xs text-slate-500">
                Assign only the permissions required by the recipient.
              </p>
            </div>

            {errorMessage && (
              <div
                className="flex gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
                role="alert"
              >
                <AlertCircle
                  size={18}
                  className="mt-0.5 shrink-0"
                />

                {errorMessage}
              </div>
            )}

            {successResult && (
              <div
                className="rounded-xl border border-emerald-200 bg-emerald-50 p-4"
                role="status"
              >
                <div className="flex items-center gap-2 font-semibold text-emerald-800">
                  <CheckCircle2 size={19} />
                  Invitation email sent successfully!
                </div>

                <p className="mt-2 text-sm text-emerald-700">
                  A six-digit verification code has been sent to{" "}
                  <strong>{successResult.email}</strong>.
                </p>

                <p className="mt-2 flex items-center gap-2 text-xs text-emerald-700">
                  <Clock size={14} />

                  Expires:{" "}
                  {new Date(
                    successResult.expires_at,
                  ).toLocaleString()}
                </p>
              </div>
            )}

            <Button
              type="submit"
              size="lg"
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? (
                <>
                  <span className="button-spinner" />
                  Sending invitation...
                </>
              ) : (
                <>
                  <MailPlus size={18} />
                  Send invitation
                </>
              )}
            </Button>
          </form>
        </div>

        {/* Information panel */}

        <div className="grid content-start gap-4">

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <ShieldCheck
              size={25}
              className="text-violet-600"
            />

            <h3 className="mt-4 font-bold text-slate-900">
              Secure invitations
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              Invitations are restricted to workspace administrators.
              Each verification code is single-use and stored securely
              as a hash.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <Clock
              size={25}
              className="text-cyan-600"
            />

            <h3 className="mt-4 font-bold text-slate-900">
              OTP expiration
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              Registration codes expire after 10 minutes.
              Previous unused codes are invalidated when a new
              invitation is successfully issued.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <Users
              size={25}
              className="text-blue-600"
            />

            <h3 className="mt-4 font-bold text-slate-900">
              Role management
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              Assign administrator, operator or viewer access
              according to the responsibilities of each user.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}