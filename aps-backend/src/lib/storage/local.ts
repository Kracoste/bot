import { promises as fs } from "fs";
import path from "path";

const UPLOAD_DIR = path.join(process.cwd(), "uploads");

export async function ensureUploadDir(): Promise<void> {
  await fs.mkdir(UPLOAD_DIR, { recursive: true });
}

export async function saveBuffer(
  buffer: Buffer,
  fileName: string,
): Promise<string> {
  await ensureUploadDir();
  const targetPath = path.join(UPLOAD_DIR, fileName);
  await fs.writeFile(targetPath, buffer);
  return targetPath;
}
