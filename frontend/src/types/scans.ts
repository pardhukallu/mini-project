export interface BreachedAccount {
  name: string;
  title: string;
  domain: string;
  breach_date: string;
  added_date?: string;
  pwn_count: number;
  description: string;
  logo_path?: string;
  data_classes: string[];
  is_verified: boolean;
  is_sensitive: boolean;
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

