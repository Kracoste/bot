import { NextResponse } from "next/server";
import { z } from "zod";
import { findFile } from "@/lib/repository/fileRepository";
import { routeToPipeline } from "@/lib/processors/pipelineRouter";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const bodySchema = z.object({
  fileId: z.string().uuid(),
});

export async function POST(request: Request) {
  try {
    const json = await request.json();
    const parsed = bodySchema.safeParse(json);
    if (!parsed.success) {
      return NextResponse.json(
        { error: "Requête invalide", details: parsed.error.flatten() },
        { status: 400 },
      );
    }

    const file = await findFile(parsed.data.fileId);
    if (!file) {
      return NextResponse.json(
        { error: "Fichier introuvable" },
        { status: 404 },
      );
    }

    const pipelineResult = await routeToPipeline(file);
    return NextResponse.json(pipelineResult);
  } catch (error) {
    console.error("Process error", error);
    return NextResponse.json(
      { error: "Impossible de lancer le traitement." },
      { status: 500 },
    );
  }
}
