import { z } from "zod";

export const disruptionFormSchema = z.object({
  supplier_id: z
    .string()
    .trim()
    .min(1, "Supplier ID is required")
    .refine((val) => ["SUP-01", "SUP-02"].includes(val), {
      message: "Supplier must be a valid Tier-1 supplier (SUP-01 or SUP-02)",
    }),
  disruption_type: z.enum(["SUPPLIER_DELAY", "CAPACITY_DROP", "FORCE_MAJEURE"], {
    required_error: "Disruption type is required",
  }),
  delay_duration_hours: z
    .number({ invalid_type_error: "Delay duration must be a numeric value" })
    .finite("Delay duration must be finite")
    .gt(0, "Delay duration must be greater than 0 hours")
    .max(720, "Delay duration cannot exceed 720 hours"),
  description: z.string().max(240, "Description cannot exceed 240 characters"),
});

export type DisruptionFormValues = z.infer<typeof disruptionFormSchema>;

