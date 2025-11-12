import { NextResponse } from "next/server";
import { findFile } from "@/lib/repository/fileRepository";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const fileId = searchParams.get("fileId");

  if (!fileId) {
    return NextResponse.json(
      { error: "Paramètre fileId requis." },
      { status: 400 },
    );
  }

  const file = await findFile(fileId);
  if (!file) {
    return NextResponse.json({ error: "Fichier introuvable." }, { status: 404 });
  }

  return NextResponse.json({ urn: file.urn ?? null });
}
