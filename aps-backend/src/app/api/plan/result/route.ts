import { NextResponse } from "next/server";
import { findByJob } from "@/lib/repository/fileRepository";
import { promises as fs } from "fs";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get("jobId");

  if (!jobId) {
    return NextResponse.json(
      { error: "Paramètre jobId requis." },
      { status: 400 },
    );
  }

  const file = await findByJob(jobId);
  if (!file) {
    return NextResponse.json({ error: "Job introuvable." }, { status: 404 });
  }

  if (file.status !== "processed" || !file.resultPath) {
    return NextResponse.json(
      { status: file.status, message: "Traitement en cours..." },
      { status: 202 },
    );
  }

  const payload = await fs.readFile(file.resultPath, "utf-8");
  return NextResponse.json(JSON.parse(payload));
}
