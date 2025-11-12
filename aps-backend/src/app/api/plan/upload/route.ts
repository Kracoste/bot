import { NextResponse } from "next/server";
import path from "path";
import crypto from "crypto";
import { saveBuffer } from "@/lib/storage/local";
import { detectFileKind } from "@/lib/detectors/fileType";
import { saveFile } from "@/lib/repository/fileRepository";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!(file instanceof File)) {
      return NextResponse.json(
        { error: "Le champ 'file' est requis." },
        { status: 400 },
      );
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const originalName = file.name ?? "plan";
    const ext = path.extname(originalName) || "";
    const fileId = crypto.randomUUID();
    const storedPath = await saveBuffer(buffer, `${fileId}${ext}`);
    const typeHint = detectFileKind(originalName, file.type ?? "");

    await saveFile({
      id: fileId,
      originalName,
      mimeType: file.type ?? "application/octet-stream",
      ext,
      size: file.size,
      storagePath: storedPath,
      createdAt: new Date().toISOString(),
      typeHint,
      status: "uploaded",
      urn: null,
    });

    return NextResponse.json({ fileId, typeHint });
  } catch (error) {
    console.error("Upload error", error);
    return NextResponse.json(
      { error: "Échec de l'envoi du plan." },
      { status: 500 },
    );
  }
}
