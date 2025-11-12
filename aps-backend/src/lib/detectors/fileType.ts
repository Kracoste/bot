import path from "path";
import type { FileKind } from "../repository/fileRepository";

const VECTOR_MIME_HINTS = ["application/postscript", "application/pdf"];

export function detectFileKind(fileName: string, mimeType: string): FileKind {
  const ext = path.extname(fileName).toLowerCase();

  if (ext === ".rvt") return "RVT";
  if (ext === ".dwg") return "DWG";
  if (ext === ".ifc") return "IFC";

  if (ext === ".pdf") {
    return VECTOR_MIME_HINTS.includes(mimeType) ? "PDF_VECTOR" : "PDF_IMAGE";
  }

  if ([".jpg", ".jpeg", ".png", ".tiff", ".bmp"].includes(ext)) {
    return "IMAGE";
  }

  return "IMAGE";
}
