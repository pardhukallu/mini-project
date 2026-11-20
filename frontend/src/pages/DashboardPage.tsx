import React, { useEffect, useState } from 'react';
import { Mail, Globe2, Puzzle, RefreshCw, ArrowUpRight, ShieldCheck, Activity, Sparkles, Radar, ScanLine } from 'lucide-react';
import { getDashboardOverviewApi } from '../api/auth';
import type { DashboardOverview } from '../types/auth';
import { useAuth } from '../context/AuthContext';
import { SecurityScoreGauge } from '../components/dashboard/SecurityScoreGauge';
import { ExposureBreakdownChart } from '../components/dashboard/ExposureBreakdownChart';
import { RecentScansTable } from '../components/dashboard/RecentScansTable';
import { ScoreTrendChart } from '../components/dashboard/ScoreTrendChart';
import { CoreSweepPanel } from '../components/dashboard/CoreSweepPanel';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = async () => {
    setIsLoading(true); setError(null);
    try { setData(await getDashboardOverviewApi()); }
    catch (err: unknown) { setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data'); }
    finally { setIsLoading(false); }
  };
  useEffect(() => { fetchOverview(); }, []);

  const metrics = [
    { title: 'Email exposures', value: data?.metrics.total_breaches ?? 0, note: 'Confirmed breach records', icon: Mail, tone: 'violet' },
    { title: 'Public footprint', value: data?.metrics.footprint_exposures ?? 0, note: 'Profiles and DNS findings', icon: Globe2, tone: 'blue' },
    { title: 'Permission risks', value: data?.metrics.high_risk_permissions ?? 0, note: 'High-impact browser access', icon: Puzzle, tone: 'mint' },
  ];

  return (
    <div className="sw-dashboard">
      <section className="sw-welcome">
        <div className="sw-welcome-copy">
          <div className="sw-eyebrow"><span className="sw-eyebrow-dot" /> PERSONAL SECURITY INTELLIGENCE</div>
          <h1>Your digital life,<br /><span>under a closer watch.</span></h1>
          <p>One clear view of your exposed data, public footprint and browser privacy.</p>
          <div className="sw-welcome-meta"><span className="sw-live-dot" /> Monitoring account <b>{user?.email}</b></div>
        </div>
        <div className="sw-orbit-scene" aria-hidden="true">
          <div className="sw-orbit sw-orbit-one" /><div className="sw-orbit sw-orbit-two" /><div className="sw-orbit sw-orbit-three" />
          <div className="sw-orbit-core"><div className="sw-core-glow" /><ShieldCheck size={43} strokeWidth={1.25} /></div>
          <div className="sw-orbit-chip chip-a"><Radar size={15}/> LIVE SCAN</div>
          <div className="sw-orbit-chip chip-b"><span className="sw-live-dot"/> PRIVATE</div>
          <div className="sw-orbit-spark spark-a" /><div className="sw-orbit-spark spark-b" />
        </div>
        <button onClick={fetchOverview} disabled={isLoading} className="sw-refresh"><RefreshCw size={15} className={isLoading ? 'animate-spin' : ''}/>{isLoading ? 'Refreshing' : 'Refresh data'}</button>
      </section>

      {error && <div className="sw-alert-error">Unable to refresh security data: {error}</div>}
      {data?.score_breakdown.verification_warnings?.length ? (
        <div className="sw-alert-warning"><b>Some checks need verification</b><ul>{data.score_breakdown.verification_warnings.map((w, i) => <li key={i}>{w.target}: {w.message}</li>)}</ul></div>
      ) : null}

      <section className="sw-stat-grid">
        {metrics.map((item, i) => {
          const Icon = item.icon;
          return <article className={`sw-stat-card tone-${item.tone}`} key={item.title} style={{ animationDelay: `${i * 90}ms` }}>
            <div className="sw-stat-top"><span>{item.title}</span><div className="sw-stat-icon"><Icon size={18}/></div></div>
            <div className="sw-stat-value">{item.value.toLocaleString()}</div>
            <div className="sw-stat-foot"><span className="sw-stat-indicator" />{item.note}<ArrowUpRight size={14}/></div>
            <div className="sw-stat-decoration" />
          </article>;
        })}
      </section>

      <section className="sw-insight-grid">
        <div className="sw-panel sw-score-panel">
          <div className="sw-section-heading"><div><div className="sw-eyebrow">YOUR SECURITY POSTURE</div><h2>Privacy health</h2></div><span className="sw-soft-pill">EVIDENCE BASED</span></div>
          <SecurityScoreGauge score={data?.metrics.privacy_score ?? 100} deductions={data?.score_breakdown.deductions ?? 0} assessed={(data?.metrics.verified_scans ?? 0) > 0} />
        </div>
        <div className="sw-panel sw-breakdown-panel">
          <div className="sw-section-heading"><div><div className="sw-eyebrow">WHERE TO FOCUS</div><h2>Exposure breakdown</h2></div><div className="sw-pulse-icon"><Activity size={17}/></div></div>
          <ExposureBreakdownChart penalties={data?.score_breakdown.category_penalties ?? { email_breaches: 0, footprint: 0, domain_security: 0, browser_permissions: 0 }} />
        </div>
      </section>

      <section className="sw-panel sw-sweep-wrap">
        <div className="sw-section-heading"><div><div className="sw-eyebrow">TAKE ACTION</div><h2>Run a security sweep</h2><p>Choose the checks you want to run. Results are saved to your account.</p></div><div className="sw-sweep-mark"><ScanLine size={22}/></div></div>
        <CoreSweepPanel onComplete={fetchOverview} />
      </section>

      <section className="sw-panel sw-trend-wrap">
        <div className="sw-section-heading"><div><div className="sw-eyebrow">OVER TIME</div><h2>Security activity</h2></div><span className="sw-soft-pill">SCAN HISTORY</span></div>
        <ScoreTrendChart history={data?.score_history ?? []} />
      </section>

      <section className="sw-panel sw-recent-wrap">
        <div className="sw-section-heading"><div><div className="sw-eyebrow">YOUR RECORD</div><h2>Recent scan activity</h2></div><div className="sw-pulse-icon"><Sparkles size={17}/></div></div>
        <RecentScansTable scans={data?.recent_scans ?? []} />
      </section>
    </div>
  );
};
