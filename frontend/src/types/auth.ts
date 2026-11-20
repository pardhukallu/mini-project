export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  message?: string;
  tokens: Tokens;
  user: User;
}

export interface RecentScan {
  id: string;
  scan_type: string;
  target: string;
  status: 'pending' | 'completed' | 'failed';
  risk_level: 'clean' | 'low' | 'medium' | 'high' | 'critical';
  score_impact: number;
  summary: string;
  created_at: string;
}

export interface DashboardOverview {
  user: {
    id: string;
    email: string;
    full_name?: string;
  };
  metrics: {
    privacy_score: number;
    total_breaches: number;
    footprint_exposures: number;
    high_risk_permissions: number;
    medium_risk_permissions: number;
    verified_scans: number;
    total_scans_performed: number;
  };
  score_breakdown: {
    base_score: number;
    deductions: number;
    category_penalties: {
      email_breaches: number;
      footprint: number;
      domain_security: number;
      browser_permissions: number;
    };
    evidence?: Array<{category:string;target:string;penalty:number;detail:string}>;
    verification_warnings?: Array<{target:string;source:string;message:string}>;
  };
  recent_scans: RecentScan[];
  score_history?: Array<{scan_id:string;created_at:string;privacy_score:number;scan_type:string}>;
}
