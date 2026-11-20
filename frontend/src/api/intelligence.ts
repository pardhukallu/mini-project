import { apiClient } from './client';
export interface ScoreData { privacy_score:number; deductions:number; category_penalties:Record<string,number>; metrics:Record<string,number>; evidence:Array<{category:string;target:string;penalty:number;detail:string}> }
export interface Recommendations { provider:string; notice:string; items:Array<{priority:string;title:string;reason:string;steps:string[]}> }
export const getScoreApi=()=>apiClient<ScoreData>('/intelligence/score');
export const getRecommendationsApi=()=>apiClient<Recommendations>('/intelligence/recommendations');
export const exportReportApi=()=>apiClient<Record<string,unknown>>('/reports/export');
