import { z } from "zod";

const envSchema = z.object({
  APS_CLIENT_ID: z.string().min(1, "APS_CLIENT_ID manquant"),
  APS_CLIENT_SECRET: z.string().min(1, "APS_CLIENT_SECRET manquant"),
  APS_BUCKET: z.string().min(1, "APS_BUCKET manquant"),
});

export type Env = z.infer<typeof envSchema>;

let cachedEnv: Env | null = null;

export function getEnv(): Env {
  if (cachedEnv) {
    return cachedEnv;
  }
  const parsed = envSchema.safeParse({
    APS_CLIENT_ID: process.env.APS_CLIENT_ID,
    APS_CLIENT_SECRET: process.env.APS_CLIENT_SECRET,
    APS_BUCKET: process.env.APS_BUCKET,
  });
  if (!parsed.success) {
    throw new Error(
      `Configuration APS incomplète: ${parsed.error.issues
        .map((issue) => issue.message)
        .join(", ")}`,
    );
  }
  cachedEnv = parsed.data;
  return parsed.data;
}
