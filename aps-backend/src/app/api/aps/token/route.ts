import { NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

export const runtime = "nodejs";

const APS_TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token";

export async function POST() {
  try {
    const env = getEnv();
    const body = new URLSearchParams({
      grant_type: "client_credentials",
      scope: "data:read data:write bucket:create bucket:read",
      client_id: env.APS_CLIENT_ID,
      client_secret: env.APS_CLIENT_SECRET,
    });

    const response = await fetch(APS_TOKEN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: "APS token request failed", details: errorText },
        { status: response.status },
      );
    }

    const tokenPayload = await response.json();
    return NextResponse.json(tokenPayload);
  } catch (error) {
    console.error("APS token error", error);
    return NextResponse.json(
      { error: "Unable to fetch APS token" },
      { status: 500 },
    );
  }
}
