import React, { useRef, useState } from 'react';
import {
  Mail,
  Search,
  ShieldCheck,
  AlertOctagon,
  Calendar,
  Users,
  ShieldAlert,
  Info,
  Lock,
} from 'lucide-react';
import { scanEmailBreachesApi } from '../../api/scans';
import type { EmailBreachResult } from '../../types/scans';
import { useAuth } from '../../context/AuthContext';
import { validateEmail } from '../../utils/email';

export const EmailBreachScanner: React.FC = () => {
  const { user } = useAuth();
  const [emailInput, setEmailInput] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<EmailBreachResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const requestInFlight = useRef(false);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (requestInFlight.current) return;

    const normalizedEmail = emailInput.trim().toLowerCase();
    setResult(null);
    setError(null);

    // Validate before sending anything to the backend/API.
    const validationError = validateEmail(normalizedEmail);
    if (validationError) {
      setError(validationError);
      return;
    }

    requestInFlight.current = true;
    setIsScanning(true);
    try {
      const data = await scanEmailBreachesApi(normalizedEmail);
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '';
      setError(
        message && !message.includes('temporarily unavailable')
          ? message
          : 'Breach checking is temporarily unavailable. Please try again.'
      );
    } finally {
      requestInFlight.current = false;
      setIsScanning(false);
    }
  };

  const handleUseCurrentEmail = () => {
    if (user?.email) {
      setEmailInput(user.email);
    }
  };

  // XposedOrNot free email-check results contain breach names, not HTML descriptions.
  const sanitizeDescription = (html: string) => {
    return html.replace(/<[^>]*>?/gm, '');
  };

  return (
    <div className="space-y-6">
      {/* Search Bar Card */}
      <div className="bg-navy-850 border border-navy-700/80 rounded-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-navy-800 pb-4 mb-5">
          <div>
            <h2 className="text-sm font-mono font-semibold uppercase tracking-wider text-slate-100 flex items-center space-x-2">
              <Mail className="w-4 h-4 text-teal-400" />
              <span>Email Data Breach Registry Auditor</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Check whether an email address appears in known public data breaches.
            </p>
          </div>

          <div className="flex items-center space-x-1.5 text-[11px] font-mono text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded border border-teal-500/20">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>XPOSEDORNOT LIVE API</span>
          </div>
        </div>

        <form onSubmit={handleScan} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="text"
                inputMode="email"
                autoComplete="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                placeholder="target-email@domain.com"
                className="w-full bg-navy-900 border border-navy-700 rounded-md pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500 font-mono transition"
              />
            </div>

            <button
              type="submit"
              disabled={isScanning}
              className="bg-teal-500 hover:bg-teal-400 disabled:bg-teal-800/60 disabled:cursor-not-allowed text-navy-950 font-semibold font-mono text-xs px-6 py-2.5 rounded-md transition flex items-center justify-center space-x-2 shrink-0"
            >
              <Search className="w-4 h-4" />
              <span>{isScanning ? 'SEARCHING REGISTRIES...' : 'AUDIT EMAIL'}</span>
            </button>
          </div>

          {user?.email && (
            <div className="flex items-center justify-between text-xs font-mono text-slate-500 pt-1">
              <span>Account Identity: {user.email}</span>
              <button
                type="button"
                onClick={handleUseCurrentEmail}
                className="text-teal-400 hover:text-teal-300 underline underline-offset-4"
              >
                Scan My Registered Email
              </button>
            </div>
          )}
        </form>
      </div>

      {error && (
        <div className="p-4 rounded bg-red-950/40 border border-red-500/30 text-xs font-mono text-red-300 flex items-center space-x-2">
          <AlertOctagon className="w-4 h-4 shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          <div
            className={`p-3 rounded border text-xs ${
              result.email_verification === 'valid'
                ? 'border-emerald-500/20 bg-emerald-950/10 text-emerald-200'
                : 'border-amber-500/20 bg-amber-950/10 text-amber-200'
            }`}
          >
            Live breach-record lookup via XposedOrNot.{' '}
            {result.email_verification === 'valid'
              ? 'The recipient mail server accepted this mailbox address.'
              : result.email_verification === 'unknown'
                ? result.email_verification_reason || 'Mailbox existence could not be confirmed.'
                : 'Mailbox existence was not verified, so this does not confirm the address is valid.'}
          </div>
          {/* Summary Metric Header */}
          <div className="bg-navy-850 border border-navy-700/80 rounded-lg p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-navy-800 pb-4">
              <div>
                <span className="text-[11px] font-mono text-slate-400 uppercase">
                  Target Audited
                </span>
                <div className="text-base font-bold font-mono text-slate-100">
                  {result.email}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">
                    Breach Status
                  </span>
                  <div>
                    {result.is_breached ? (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-xs font-mono font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        <span>{`${result.breach_count} BREACHES DETECTED`}</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-xs font-mono font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                        <Info className="w-3.5 h-3.5" />
                        <span>{result.source === 'xposedornot_api' ? 'NOT FOUND IN BREACH DATA' : 'NO VERIFIED LIVE RESULT'}</span>
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-right border-l border-navy-800 pl-4">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">
                    Score Deduction
                  </span>
                  <div className="text-sm font-bold font-mono text-rose-400">
                    {result.score_impact > 0 ? `-${result.score_impact} pts` : '0 pts'}
                  </div>
                </div>
              </div>
            </div>

            {/* Compromised Data Classes */}
            {result.compromised_data_classes.length > 0 && (
              <div className="mt-4 pt-2">
                <span className="text-[11px] font-mono text-slate-400 uppercase block mb-2">
                  Exposed Data Attributes
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result.compromised_data_classes.map((cls) => {
                    const isSensitive = cls.toLowerCase().includes('password') || cls.toLowerCase().includes('pin');
                    return (
                      <span
                        key={cls}
                        className={`text-[11px] font-mono px-2 py-0.5 rounded border ${
                          isSensitive
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/30 font-medium'
                            : 'bg-navy-900 text-slate-300 border-navy-700'
                        }`}
                      >
                        {cls}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Detailed Breaches List */}
          {result.breaches.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
                Breach Names Reported ({result.breaches.length})
              </h3>
              <div className="grid grid-cols-1 gap-4">
                {result.breaches.map((breach) => (
                  <div
                    key={breach.name}
                    className="bg-navy-850 border border-navy-700/80 rounded-lg p-5 space-y-3"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-navy-800 pb-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded bg-navy-900 border border-navy-800 flex items-center justify-center font-mono font-bold text-teal-400 text-xs">
                          {breach.name.slice(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold font-mono text-slate-100">
                            {breach.title || breach.name}
                          </h4>
                          {breach.domain && <span className="text-xs text-slate-500 font-mono">{breach.domain}</span>}
                        </div>
                      </div>

                      <div className="flex items-center space-x-4 text-xs font-mono text-slate-400">
                        {breach.breach_date && <div className="flex items-center space-x-1.5"><Calendar className="w-3.5 h-3.5 text-slate-500" /><span>Breached: {breach.breach_date}</span></div>}
                        {typeof breach.pwn_count === 'number' && breach.pwn_count > 0 && <div className="flex items-center space-x-1.5"><Users className="w-3.5 h-3.5 text-slate-500" /><span>{breach.pwn_count.toLocaleString()} accounts</span></div>}
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 leading-relaxed">
                      {breach.description ? sanitizeDescription(breach.description) : 'Breach name reported by XposedOrNot.'}
                    </p>

                    <div className="pt-2 border-t border-navy-800/80 flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap gap-1">
                        {(breach.data_classes?.length ?? 0) > 0 ? breach.data_classes.map((item) => (
                          <span key={item} className="text-[10px] font-mono px-2 py-0.5 rounded bg-navy-900 border border-navy-800 text-slate-400">{item}</span>
                        )) : <span className="text-[10px] text-slate-500">Free endpoint provides breach names only; detailed metadata unavailable.</span>}
                      </div>

                      <div className="flex items-center space-x-1.5 text-[11px] font-mono text-amber-400">
                        <Lock className="w-3 h-3" />
                        <span>Change Password Recommended</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-navy-850 border border-amber-500/20 rounded-lg p-10 text-center">
              <Info className="w-10 h-10 text-amber-300 mx-auto mb-3" />
              <h3 className="text-sm font-mono font-semibold text-slate-200">
                {result.source === 'xposedornot_api' ? 'Not Found in Breach Data' : 'No Verified Live Result'}
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                {result.email_verification === 'valid'
                  ? 'This address was not found in known breach records. The recipient mail server accepted the mailbox address.'
                  : result.email_verification === 'unknown'
                    ? 'This address was not found in known breach records, but mailbox existence could not be confirmed.'
                    : 'This address was not found in known breach records. Mailbox existence was not verified, so this does not confirm the address is valid.'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
