import { useState } from "react";
import { Globe, AlertCircle, CheckCircle, XCircle, Loader2, ShieldAlert } from "lucide-react";
import { auditDomainApi } from "../../api/footprint";
import type { DomainAuditResult, DnsRecordCheck } from "../../types/footprint";

const RISK_STYLES: Record<string, string> = {
  none: "text-teal-400 bg-teal-900/20 border-teal-700/40",
  low: "text-yellow-400 bg-yellow-900/20 border-yellow-700/40",
  medium: "text-orange-400 bg-orange-900/20 border-orange-700/40",
  high: "text-red-400 bg-red-900/20 border-red-700/40",
};

const RISK_LABELS: Record<string, string> = {
  none: "SECURE",
  low: "LOW RISK",
  medium: "MEDIUM RISK",
  high: "HIGH RISK",
};

function RecordRow({ check }: { check: DnsRecordCheck }) {
  const icon = check.present ? (
    <CheckCircle className="w-4 h-4 text-teal-400" />
  ) : check.risk_level === "low" ? (
    <AlertCircle className="w-4 h-4 text-yellow-500" />
  ) : (
    <XCircle className="w-4 h-4 text-red-400" />
  );

  return (
    <tr className="border-b border-slate-700/40 hover:bg-slate-800/30 transition-colors">
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-mono text-sm font-semibold text-slate-200">{check.record_type}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        <span className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold border ${RISK_STYLES[check.risk_level]}`}>
          {RISK_LABELS[check.risk_level]}
        </span>
      </td>
      <td className="px-4 py-3">
        {check.policy && (
          <span className="font-mono text-xs text-slate-400 mr-2 px-1.5 py-0.5 bg-slate-700/50 rounded">
            {check.policy}
          </span>
        )}
      </td>
      <td className="px-4 py-3 text-xs text-slate-400 max-w-xs">{check.note}</td>
      <td className="px-4 py-3">
        {check.value && (
          <span className="font-mono text-xs text-slate-500 truncate max-w-[200px] block" title={check.value}>
            {check.value.length > 50 ? check.value.slice(0, 50) + "…" : check.value}
          </span>
        )}
      </td>
    </tr>
  );
}

export default function DomainAuditComponent() {
  const [domain, setDomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DomainAuditResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!domain.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await auditDomainApi(domain.trim());
      setResult(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Audit failed. Please check the domain and try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const overallRisk = result?.overall_risk ?? "none";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-slate-100">Domain Security Audit</h2>
        <p className="text-sm text-slate-400 mt-1">
          Checks SPF, DMARC, DKIM, and MX records for your domain using live DNS queries. No API key required.
        </p>
      </div>

      {/* Input */}
      <form onSubmit={handleAudit} className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="e.g. gmail.com"
            className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500/30 font-mono"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !domain.trim()}
          className="px-5 py-2.5 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Auditing…
            </>
          ) : (
            "Audit DNS"
          )}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-900/20 border border-red-700/40 rounded-lg text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Overall risk banner */}
          <div className={`flex items-center justify-between p-4 rounded-lg border ${RISK_STYLES[overallRisk]}`}>
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-5 h-5" />
              <div>
                <div className="text-sm font-semibold">{result.domain}</div>
                <div className="text-xs opacity-70">Overall email security posture</div>
              </div>
            </div>
            <span className="text-lg font-bold font-mono">{RISK_LABELS[overallRisk]}</span>
          </div>

          {/* MX records */}
          {result.mx_records.length > 0 && (
            <div className="p-3 bg-slate-800/60 border border-slate-700/50 rounded-lg">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">MX Records</div>
              <div className="flex flex-wrap gap-2">
                {result.mx_records.map((mx) => (
                  <span key={mx} className="font-mono text-xs text-slate-300 px-2 py-1 bg-slate-700/60 rounded border border-slate-600/50">
                    {mx}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* DNS check table */}
          <div className="border border-slate-700/50 rounded-lg overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-slate-800/80 border-b border-slate-700/50">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Record</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Risk</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Policy</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Finding</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Record Value</th>
                </tr>
              </thead>
              <tbody>
                {result.checks.map((c) => (
                  <RecordRow key={c.record_type} check={c} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
