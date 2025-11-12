import type { StoredFile } from "../repository/fileRepository";
import { updateFile } from "../repository/fileRepository";
import {
  createSignedUrl,
  downloadObjectToPath,
} from "./ossClient";
import { runDesignAutomationWorkItem } from "./designAutomationRunner";
import type { WorkItemLaunch } from "./designAutomationRunner";

type ActivityConfig = {
  activityId: string;
  inputName: string;
  outputName: string;
};

const ACTIVITY_MAP: Record<string, ActivityConfig> = {
  RVT: {
    activityId: process.env.REVIT_ACTIVITY_ID ?? "LBF-Revit-Rooms-v1",
    inputName: "inputRvt",
    outputName: "outputJson",
  },
  DWG: {
    activityId: process.env.ACAD_ACTIVITY_ID ?? "LBF-Acad-Rooms-v1",
    inputName: "inputDwg",
    outputName: "outputJson",
  },
  PDF_VECTOR: {
    activityId: process.env.ACAD_ACTIVITY_ID ?? "LBF-Acad-Rooms-v1",
    inputName: "inputDwg",
    outputName: "outputJson",
  },
};

export async function runDesignAutomationJob(params: {
  file: StoredFile;
  jobId: string;
  objectKey: string;
  resultPath: string;
}): Promise<void> {
  const { file, jobId, objectKey, resultPath } = params;
  const config = ACTIVITY_MAP[file.typeHint];

  if (!config) {
    await markAsFailed(file.id, `No activity configured for ${file.typeHint}`);
    return;
  }

  try {
    const inputUrl = await createSignedUrl(objectKey, "read");
    const outputObjectKey = `${jobId}-rooms.json`;
    const outputUrl = await createSignedUrl(outputObjectKey, "write");

    const launch: WorkItemLaunch = {
      activityId: config.activityId,
      arguments: {
        [config.inputName]: { verb: "get", url: inputUrl },
        [config.outputName]: { verb: "put", url: outputUrl },
      },
      outputObjectKey,
      resultPath,
    };

    await runDesignAutomationWorkItem(launch);
    await downloadObjectToPath(outputObjectKey, resultPath);

    await updateFile(file.id, (current) => ({
      ...current,
      status: "processed",
      resultPath,
    }));
  } catch (error) {
    console.error("Design Automation job failed", error);
    await markAsFailed(file.id, String(error));
  }
}

async function markAsFailed(fileId: string, message: string): Promise<void> {
  await updateFile(fileId, (current) => ({
    ...current,
    status: "failed",
    resultPath: message,
  }));
}
