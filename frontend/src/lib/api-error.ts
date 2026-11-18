interface FastApiDetailItem {
  msg?: unknown;
  loc?: unknown;
}

interface ApiErrorLike {
  message?: unknown;
  code?: unknown;
  response?: {
    data?: {
      detail?: unknown;
      message?: unknown;
    };
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function formatDetail(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item: FastApiDetailItem) => (typeof item?.msg === "string" ? item.msg : null))
      .filter((item): item is string => Boolean(item));
    if (messages.length > 0) return messages.join(" ");
  }

  return null;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (isRecord(error)) {
    const candidate = error as ApiErrorLike;
    const detail = candidate.response?.data?.detail;
    const formattedDetail = formatDetail(detail);
    if (formattedDetail) return formattedDetail;

    const responseMessage = candidate.response?.data?.message;
    if (typeof responseMessage === "string" && responseMessage.trim()) {
      return responseMessage;
    }

    if (candidate.code === "ECONNABORTED") {
      return "The request timed out. Please try again.";
    }

    if (typeof candidate.message === "string" && candidate.message.trim()) {
      if (candidate.message.toLowerCase().includes("network error")) {
        return "Unable to reach AgentOps-OS. Check that the backend is running.";
      }
    }
  }

  return fallback;
}
