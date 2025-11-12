import { promises as fs } from "fs";
import path from "path";

const DATA_DIR = path.join(process.cwd(), "data");
const FILE_DB = path.join(DATA_DIR, "files.json");

export type FileKind = "RVT" | "DWG" | "IFC" | "PDF_VECTOR" | "PDF_IMAGE" | "IMAGE";

export interface StoredFile {
  id: string;
  originalName: string;
  mimeType: string;
  ext: string;
  size: number;
  storagePath: string;
  createdAt: string;
  typeHint: FileKind;
  status: "uploaded" | "processing" | "processed" | "failed";
  jobId?: string;
  urn?: string | null;
  resultPath?: string;
}

async function ensureDb(): Promise<void> {
  try {
    await fs.access(FILE_DB);
  } catch {
    await fs.mkdir(DATA_DIR, { recursive: true });
    await fs.writeFile(FILE_DB, "[]", "utf-8");
  }
}

async function readAll(): Promise<StoredFile[]> {
  await ensureDb();
  const raw = await fs.readFile(FILE_DB, "utf-8");
  return JSON.parse(raw) as StoredFile[];
}

async function writeAll(entries: StoredFile[]): Promise<void> {
  await fs.writeFile(FILE_DB, JSON.stringify(entries, null, 2), "utf-8");
}

export async function saveFile(entry: StoredFile): Promise<void> {
  const entries = await readAll();
  entries.push(entry);
  await writeAll(entries);
}

export async function updateFile(
  id: string,
  updater: (current: StoredFile) => StoredFile,
): Promise<StoredFile> {
  const entries = await readAll();
  const index = entries.findIndex((f) => f.id === id);
  if (index === -1) {
    throw new Error(`Fichier ${id} introuvable`);
  }
  const updated = updater(entries[index]);
  entries[index] = updated;
  await writeAll(entries);
  return updated;
}

export async function findFile(id: string): Promise<StoredFile | undefined> {
  const entries = await readAll();
  return entries.find((f) => f.id === id);
}

export async function findByJob(jobId: string): Promise<StoredFile | undefined> {
  const entries = await readAll();
  return entries.find((f) => f.jobId === jobId);
}
