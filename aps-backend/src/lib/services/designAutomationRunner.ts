import { setTimeout as delay } from "timers/promises";
import { getEnv } from "../env";

const DA_BASE = "https://developer.api.autodesk.com/da/us-east/v3";

interface TokenState {
  token: string;
  expiresAt: number;
}

let cachedToken: TokenState | null = null;

async function getToken(scope: string): Promise<string> {
  const now = Date.now();
  if (cachedToken && now < cachedToken.expiresAt - 60 * 1000) {
    return cachedToken.token;
  }

  const env = getEnv();
  const body = new URLSearchParams({
    grant_type: "client_credentials",
    client_id: env.APS_CLIENT_ID,
    client_secret: env.APS_CLIENT_SECRET,
    scope,
  });

  const response = await fetch("https://developer.api.autodesk.com/authentication/v2/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) {
    throw new Error(`APS token failed: ${response.statusText}`);
  }
  const payload = await response.json();
  cachedToken = {
    token: payload.access_token,
    expiresAt: now + payload.expires_in * 1000,
  };
  return payload.access_token;
}

export interface WorkItemLaunch {
  activityId: string;
  arguments: Record<string, { verb: "get" | "put"; url: string }>;
  outputObjectKey: string;
  resultPath: string;
}

export async function runDesignAutomationWorkItem(
  launch: WorkItemLaunch,
): Promise<void> {
  const token = await getToken("code:all data:read data:write bucket:read bucket:create");

  const response = await fetch(`${DA_BASE}/workitems`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      activityId: launch.activityId,
      arguments: launch.arguments,
    }),
  });

  if (!response.ok) {
    throw new Error(`WorkItem launch failed: ${await response.text()}`);
  }

  const payload = await response.json();
  await pollWorkItem(payload.id as string, token);
}

async function pollWorkItem(workItemId: string, token: string): Promise<void> {
  for (;;) {
    await delay(5000);
    const response = await fetch(`${DA_BASE}/workitems/${workItemId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error(`Polling WorkItem failed: ${await response.text()}`);
    }
    const payload = await response.json();
    const status = payload.status as string;
    if (status === "success") {
      return;
    }
    if (status === "failed" || status === "cancelled") {
      throw new Error(`WorkItem ${workItemId} ended with status ${status}: ${payload.statusDetails ?? ""}`);
    }
  }
}
