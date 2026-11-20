// Phase 3 — Footprint API client

import { apiClient } from "./client";
import type { UsernameCheckResult, DomainAuditResult } from "../types/footprint";

export async function scanUsernameApi(username: string): Promise<UsernameCheckResult> {
  return apiClient<UsernameCheckResult>("/footprint/username-scan", {
    method: "POST",
    body: JSON.stringify({ username }),
    requiresAuth: true,
  });
}

export async function auditDomainApi(domain: string): Promise<DomainAuditResult> {
  return apiClient<DomainAuditResult>("/footprint/domain-audit", {
    method: "POST",
    body: JSON.stringify({ domain }),
    requiresAuth: true,
  });
}
