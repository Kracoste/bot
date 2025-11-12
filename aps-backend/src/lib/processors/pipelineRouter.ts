import crypto from "crypto";
import path from "path";
import { promises as fs } from "fs";
import type { FileKind, StoredFile } from "../repository/fileRepository";
import { updateFile } from "../repository/fileRepository";

export interface PipelineResult {
  jobId: string;
  pipeline: FileKind;
}

export async function routeToPipeline(file: StoredFile): Promise<PipelineResult> {
  const jobId = `job_${crypto.randomUUID()}`;

  // TODO: intégrer les appels réels à APS. Pour le MVP, on simule le résultat.
  const fakeRooms = [
    {
      name: `${path.parse(file.originalName).name}-Room-1`,
      area_m2: 12.5,
      perimeter_m: 14.0,
      bbox: { min: [0, 0], max: [4, 5] },
      source: file.typeHint,
    },
  ];

  const jobPath = path.join(process.cwd(), "data", "jobs", `${jobId}.json`);
  await fs.writeFile(
    jobPath,
    JSON.stringify({ fileId: file.id, rooms: fakeRooms }, null, 2),
    "utf-8",
  );

  await updateFile(file.id, (current) => ({
    ...current,
    status: "processed",
    jobId,
    resultPath: jobPath,
  }));

  return { jobId, pipeline: file.typeHint };
}
