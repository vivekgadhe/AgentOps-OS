import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "./api-error";

describe("getApiErrorMessage", () => {
  it("returns a FastAPI string detail", () => {
    expect(
      getApiErrorMessage(
        { response: { data: { detail: "Invalid email or password" } } },
        "Fallback",
      ),
    ).toBe("Invalid email or password");
  });

  it("joins validation messages returned by FastAPI", () => {
    expect(
      getApiErrorMessage(
        {
          response: {
            data: {
              detail: [
                { msg: "Enter a valid email address" },
                { msg: "Password is required" },
              ],
            },
          },
        },
        "Fallback",
      ),
    ).toBe("Enter a valid email address Password is required");
  });

  it("provides a useful message for an unavailable backend", () => {
    expect(
      getApiErrorMessage({ message: "Network Error" }, "Fallback"),
    ).toBe("Unable to reach AgentOps-OS. Check that the backend is running.");
  });

  it("uses the fallback for unrecognized errors", () => {
    expect(getApiErrorMessage(null, "Please try again.")).toBe("Please try again.");
  });
});
