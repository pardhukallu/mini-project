import { useState } from "react";
import { Search, ExternalLink, CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react";
import { scanUsernameApi } from "../../api/footprint";
import type { UsernameCheckResult, PlatformPresence } from "../../types/footprint";

function PlatformRow({ p }: { p: PlatformPresence }) {
  const statusIcon = p.present ? (
    <CheckCircle className="w-4 h-4 text-red-400" />
  ) : !p.verified ? (
    <AlertCircle className="w-4 h-4 text-yellow-500" />
  ) : (
    <XCircle className="w-4 h-4 text-teal-500" />
  );

  const rowClass = p.present
    ? "bg-red-900/10 border-red-800/30"
    : "bg-transparent border-slate-700/40";

  return (
    <tr className={`border-b ${rowClass} transition-colors`}>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          {statusIcon}
          <span className="text-sm font-medium text-slate-200">{p.platform}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        {p.present ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-red-900/40 text-red-300 border border-red-700/40">
            EXPOSED
          </span>
        ) : !p.verified ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-yellow-900/30 text-yellow-400 border border-yellow-700/40">
            UNVERIFIABLE
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-teal-900/30 text-teal-400 border border-teal-700/40">
            NOT FOUND
          </span>
        )}
      </td>
      <td className="px-4 py-3 text-xs text-slate-400 font-mono">{p.note ?? "—"}</td>
      <td className="px-4 py-3">
        <a
          href={p.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-teal-400 transition-colors"
        >
          View <ExternalLink className="w-3 h-3" />
        </a>
      </td>
    </tr>
  );
}

export default function UsernameScannerComponent() {
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UsernameCheckResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await scanUsernameApi(username.trim());
      setResult(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Scan failed. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-slate-100">Username OSINT Scanner</h2>
        <p className="text-sm text-slate-400 mt-1">
          Checks your username across {10} major platforms using public HTTP probes. No login required.
        </p>
      </div>

      {/* Input */}
      <form onSubmit={handleScan} className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. johndoe"
            className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500/30 font-mono"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !username.trim()}
          className="px-5 py-2.5 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Scanning…
            </>
          ) : (
            "Scan"
          )}
        </button>
      </form>

      {/* Notice */}
      <div className="flex items-start gap-2 p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg text-xs text-slate-400">
        <AlertCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0 text-yellow-500" />
        <span>
          Some platforms (LinkedIn, Instagram, Twitter/X) block automated checks and cannot be verified reliably.
          Only HTTP 200/404 responses are treated as found/not found. Rate limits, bot blocks, timeouts and soft-404 platforms are marked unverified.
        </span>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-900/20 border border-red-700/40 rounded-lg text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary row */}
          <div className="flex items-center gap-6 p-4 bg-slate-800/60 border border-slate-700/50 rounded-lg">
            <div>
              <div className="text-2xl font-bold text-slate-100 font-mono">{result.platforms_found}</div>
              <div className="text-xs text-slate-400">exposed platforms</div>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div>
              <div className="text-2xl font-bold text-slate-100 font-mono">{result.platforms_checked}</div>
              <div className="text-xs text-slate-400">platforms checked</div>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div>
              <div className={`text-sm font-semibold font-mono ${result.platforms_found > 0 ? "text-red-400" : "text-teal-400"}`}>
                {result.platforms_found > 0 ? "FOOTPRINT DETECTED" : result.results.some(p => !p.verified) ? "PARTIALLY UNVERIFIED" : "MINIMAL FOOTPRINT"}
              </div>
              <div className="text-xs text-slate-400 font-mono">for @{result.username}</div>
            </div>
          </div>

          {/* Results table */}
          <div className="border border-slate-700/50 rounded-lg overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-slate-800/80 border-b border-slate-700/50">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Platform</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Note</th>
                  <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Link</th>
                </tr>
              </thead>
              <tbody>
                {result.results.map((p) => (
                  <PlatformRow key={p.platform} p={p} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
