import crypto from "crypto";
import { promises as fs } from "fs";
import path from "path";
import { getEnv } from "../env";

const OSS_BASE = "https://developer.api.autodesk.com/oss/v2";

let cachedToken: { token: string; expiresAt: number } | null = null;

async function getToken(): Promise<string> {
  const now = Date.now();
  if (cachedToken && now < cachedToken.expiresAt - 60 * 1000) {
    return cachedToken.token;
  }

  const env = getEnv();
  const body = new URLSearchParams({
    grant_type: "client_credentials",
    client_id: env.APS_CLIENT_ID,
    client_secret: env.APS_CLIENT_SECRET,
    scope: "data:read data:write bucket:read bucket:create",
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

export interface UploadResult {
  objectId: string;
  objectKey: string;
}

export async function uploadLocalFileToOss(localPath: string): Promise<UploadResult> {
  const env = getEnv();
  const token = await getToken();
  const fileName = path.basename(localPath);
  const objectKey = `${crypto.randomUUID()}_${fileName}`;

  const buffer = await fs.readFile(localPath);
  const response = await fetch(`${OSS_BASE}/buckets/${env.APS_BUCKET}/objects/${encodeURIComponent(objectKey)}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/octet-stream",
    },
    body: buffer,
  });
  if (!response.ok) {
    throw new Error(`OSS upload failed: ${response.statusText}`);
  }
  const data = await response.json();
  return { objectId: data.objectId as string, objectKey };
}

export async function createSignedUrl(
  objectKey: string,
  access: "read" | "write",
  minutesExpiration = 30,
): Promise<string> {
  const env = getEnv();
  const token = await getToken();
  const response = await fetch(
    `${OSS_BASE}/buckets/${env.APS_BUCKET}/objects/${encodeURIComponent(objectKey)}/signed?access=${access}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        minutesExpiration,
        singleUse: false,
      }),
    },
  );
  if (!response.ok) {
    throw new Error(`Signed URL failed: ${response.statusText}`);
  }
  const data = await response.json();
  return data.signedUrl as string;
}

export async function downloadObjectToPath(objectKey: string, destinationPath: string): Promise<void> {
  const url = await createSignedUrl(objectKey, "read", 15);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Download failed: ${response.statusText}`);
  }
  const buffer = Buffer.from(await response.arrayBuffer());
  await fs.mkdir(path.dirname(destinationPath), { recursive: true });
  await fs.writeFile(destinationPath, buffer);
}

export async function translateFileToUrn(objectId: string): Promise<string> {
  const urn = Buffer.from(objectId).toString("base64");
  return urn.replace(/=/g, "");
}
