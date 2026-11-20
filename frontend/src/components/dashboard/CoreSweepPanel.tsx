import React, { useState } from 'react';
import { Play, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { scanEmailBreachesApi } from '../../api/scans';
import { scanUsernameApi, auditDomainApi } from '../../api/footprint';
import { useAuth } from '../../context/AuthContext';

type Outcome = { name: string; ok: boolean; detail: string };

export const CoreSweepPanel: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const { user } = useAuth();
  const [email, setEmail] = useState(user?.email ?? '');
  const [username, setUsername] = useState('');
  const [domain, setDomain] = useState('');
  const [busy, setBusy] = useState(false);
  const [outcomes, setOutcomes] = useState<Outcome[]>([]);

  const run = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setOutcomes([]);
    const jobs: Array<Promise<Outcome>> = [];
    if (email.trim()) jobs.push(scanEmailBreachesApi(email.trim()).then((result) => ({
      name: 'Email breach lookup', ok: result.source === 'xposedornot_api',
      detail: result.source === 'xposedornot_api' ? `${result.breach_count} breach record(s) returned by XposedOrNot` : 'No verified result returned',
    })).catch((error) => ({ name: 'Email breach lookup', ok: false, detail: error instanceof Error ? error.message : 'Request failed' })));
    if (username.trim()) jobs.push(scanUsernameApi(username.trim()).then((result) => ({
      name: 'Username OSINT', ok: true, detail: `${result.platforms_found} public profile(s) found · ${result.results.filter((item) => !item.verified).length} unverified`,
    })).catch((error) => ({ name: 'Username OSINT', ok: false, detail: error instanceof Error ? error.message : 'Request failed' })));
    if (domain.trim()) jobs.push(auditDomainApi(domain.trim()).then((result) => ({
      name: 'Domain DNS audit', ok: true, detail: `${result.overall_risk.toUpperCase()} · ${result.checks.length} checks completed`,
    })).catch((error) => ({ name: 'Domain DNS audit', ok: false, detail: error instanceof Error ? error.message : 'Request failed' })));
    const results = await Promise.all(jobs);
    setOutcomes(results);
    setBusy(false);
    onComplete();
  };

  return <section className="sw-panel p-6">
    <div className="flex items-start justify-between gap-3">
      <div><p className="sw-eyebrow">QUICK AUDIT</p><h3 className="text-lg font-semibold text-slate-100 mt-1">Run an exposure sweep</h3><p className="text-sm text-slate-400 mt-1">Choose the checks you want to run. Leave a field blank to skip it.</p></div>
      <span className="sw-status">USER INITIATED</span>
    </div>
    <form onSubmit={run} className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
      <label className="text-xs text-slate-400">Email address<input type="email" name="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" className="sw-input" /></label>
      <label className="text-xs text-slate-400">Public username<input type="text" name="username" autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="your_username" className="sw-input" /></label>
      <label className="text-xs text-slate-400">Domain<input type="text" name="domain" autoComplete="url" value={domain} onChange={(event) => setDomain(event.target.value)} placeholder="example.com" className="sw-input" /></label>
      <div className="md:col-span-3 flex flex-wrap items-center justify-between gap-3 pt-1"><p className="text-xs text-slate-500">Browser permission checks are started separately from the extension.</p><button disabled={busy || (!email.trim() && !username.trim() && !domain.trim())} className="sw-primary-button">{busy ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />} {busy ? 'Running checks…' : 'Run selected checks'}</button></div>
    </form>
    {outcomes.length > 0 && <div className="mt-5 border-t border-white/10 pt-4 space-y-3">{outcomes.map((outcome, index) => <div key={index} className="flex gap-3 items-start text-sm"><span className={outcome.ok ? 'text-emerald-400' : 'text-amber-400'}>{outcome.ok ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}</span><div><b className="text-slate-200">{outcome.name}</b><p className="text-slate-400 mt-0.5">{outcome.detail}</p></div></div>)}</div>}
  </section>;
};
