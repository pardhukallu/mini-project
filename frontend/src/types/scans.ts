export interface BreachedAccount {
  name: string;
  title?: string | null;
  domain?: string | null;
  breach_date?: string | null;
  added_date?: string | null;
  pwn_count?: number | null;
  description?: string | null;
  logo_path?: string | null;
  data_classes: string[];
  is_verified?: boolean | null;
  is_sensitive?: boolean | null;
}

export interface EmailBreachResult {
  email: string;
  is_breached: boolean;
  breach_count: number;
  risk_level: 'clean' | 'low' | 'medium' | 'high' | 'critical';
  score_impact: number;
  compromised_data_classes: string[];
  breaches: BreachedAccount[];
  source: 'xposedornot_api';
}
