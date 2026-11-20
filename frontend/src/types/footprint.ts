// Phase 3 — Footprint TypeScript types

export interface PlatformPresence {
  platform: string;
  url: string;
  present: boolean;
  verified: boolean;
  status_code: number | null;
  note: string | null;
}

export interface UsernameCheckResult {
  username: string;
  platforms_checked: number;
  platforms_found: number;
  results: PlatformPresence[];
  scan_id: string;
}

export interface DnsRecordCheck {
  record_type: string;       // "SPF" | "DMARC" | "DKIM" | "MX"
  present: boolean;
  value: string | null;
  policy: string | null;
  tls_supported?: boolean | null;
  risk_level: "none" | "low" | "medium" | "high";
  note: string;
}

export interface DomainAuditResult {
  domain: string;
  mx_records: string[];
  checks: DnsRecordCheck[];
  overall_risk: "none" | "low" | "medium" | "high";
  scan_id: string;
}
