import { apiClient } from './client';
import type { EmailBreachResult } from '../types/scans';
import type { RecentScan } from '../types/auth';

export async function scanEmailBreachesApi(email: string): Promise<EmailBreachResult> {
  return apiClient<EmailBreachResult>('/scans/email-breach', { method: 'POST', body: JSON.stringify({ email }), requiresAuth: true });
}


export async function getScanHistoryApi(): Promise<RecentScan[]> {
  return apiClient<RecentScan[]>('/scans/history', { method: 'GET', requiresAuth: true });
}

export async function getScanDetailApi(id: string): Promise<RecentScan & { findings_data: Record<string, unknown> }> {
  return apiClient<RecentScan & { findings_data: Record<string, unknown> }>(`/scans/${encodeURIComponent(id)}`, { method: 'GET', requiresAuth: true });
}
