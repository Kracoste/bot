import crypto from "crypto";
import path from "path";
import { promises as fs } from "fs";
import type { FileKind, StoredFile } from "../repository/fileRepository";
import { updateFile } from "../repository/fileRepository";
import { uploadLocalFileToOss, translateFileToUrn } from "../services/ossClient";
import { runDesignAutomationJob } from "../services/designAutomationClient";

export interface PipelineResult {
  jobId: string;
  pipeline: FileKind;
}

export async function routeToPipeline(file: StoredFile): Promise<PipelineResult> {
  const jobId = `job_${crypto.randomUUID()}`;

  const { objectId, objectKey } = await uploadLocalFileToOss(file.storagePath);
  const urn = await translateFileToUrn(objectId);

  const resultPath = path.join(process.cwd(), "data", "jobs", `${jobId}.json`);
  await fs.mkdir(path.dirname(resultPath), { recursive: true });

  await updateFile(file.id, (current) => ({
    ...current,
    status: "processing",
    jobId,
    urn,
  }));

  // Lancement asynchrone du job APS (revit/dwg/etc.)
  void runDesignAutomationJob({
    file,
    jobId,
    objectKey,
    resultPath,
  });

  return { jobId, pipeline: file.typeHint };
}
