import React, { useState } from 'react';
import {
  FileText,
  Mail,
  Globe,
  Puzzle,
  CheckCircle,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import type { RecentScan } from '../../types/auth';
import { getScanDetailApi } from '../../api/scans';

interface RecentScansTableProps {
  scans: RecentScan[];
}

export const RecentScansTable: React.FC<RecentScansTableProps> = ({ scans }) => {
  const [selected, setSelected] = useState<(RecentScan & {findings_data:Record<string,unknown>}) | null>(null);
  const [detailError, setDetailError] = useState('');
  const openDetail = async (id:string) => { try { setDetailError(''); setSelected(await getScanDetailApi(id)); } catch(e) { setDetailError(e instanceof Error?e.message:'Unable to load scan details'); } };
  const getScanIcon = (type: string) => {
    switch (type) {
      case 'email_breach':
        return <Mail className="w-3.5 h-3.5 text-teal-400" />;
      case 'footprint':
        return <Globe className="w-3.5 h-3.5 text-cyan-400" />;
      case 'permissions':
        return <Puzzle className="w-3.5 h-3.5 text-indigo-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'critical':
      case 'high':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>CRITICAL</span>
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>MEDIUM</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3" />
            <span>CLEAN</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-navy-850 border border-navy-700/80 rounded-lg overflow-hidden">
      <div className="p-5 border-b border-navy-800 flex items-center justify-between">
        <div>
          <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-slate-200">
            Recent Security Audits
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Immutable log of user-initiated breach and footprint scans
          </p>
        </div>
        <span className="text-[11px] font-mono text-slate-500 bg-navy-900 px-2 py-1 rounded border border-navy-800">
          LOG ENTRIES: {scans.length}
        </span>
      </div>

      {scans.length === 0 ? (
        <div className="p-12 text-center flex flex-col items-center justify-center">
          <Clock className="w-8 h-8 text-slate-600 mb-2" />
          <h4 className="text-xs font-mono font-medium text-slate-300">
            No Scan Records In Database
          </h4>
          <p className="text-xs text-slate-500 max-w-sm mt-1">
            Audit history will automatically populate when you execute email and footprint scans in Phase 2+.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-900/80 text-slate-400 text-[10px] uppercase border-b border-navy-800">
              <tr>
                <th className="py-2.5 px-4 font-medium">Type</th>
                <th className="py-2.5 px-4 font-medium">Target</th>
                <th className="py-2.5 px-4 font-medium">Risk Status</th>
                <th className="py-2.5 px-4 font-medium">Impact</th>
                <th className="py-2.5 px-4 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-800 text-slate-300">
              {scans.map((s) => (
                <tr key={s.id} onClick={() => openDetail(s.id)} title="Open scan details" className="hover:bg-navy-800/40 transition cursor-pointer">
                  <td className="py-3 px-4 flex items-center space-x-2">
                    {getScanIcon(s.scan_type)}
                    <span className="uppercase">{s.scan_type.replace('_', ' ')}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-200 font-semibold">{s.target}</td>
                  <td className="py-3 px-4">{getRiskBadge(s.risk_level)}</td>
                  <td className="py-3 px-4 font-medium">
                    {s.score_impact > 0 ? (
                      <span className="text-rose-400">-{s.score_impact} pts</span>
                    ) : (
                      <span className="text-emerald-400">0 pts</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-slate-500">
                    {new Date(s.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {detailError && <p className="p-3 text-xs text-rose-300">{detailError}</p>}
      {selected && <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label="Scan details"><div className="bg-navy-900 border border-navy-700 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto p-5"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold text-slate-100">{selected.scan_type.replaceAll('_',' ')} details</h3><p className="text-xs text-slate-400 mt-1">{selected.target} · {new Date(selected.created_at).toLocaleString()}</p></div><button onClick={()=>setSelected(null)} className="text-slate-400 hover:text-white text-sm">Close</button></div><pre className="mt-4 text-[11px] text-slate-300 bg-navy-950 border border-navy-800 rounded p-3 whitespace-pre-wrap break-words">{JSON.stringify(selected.findings_data,null,2)}</pre></div></div>}
    </div>
  );
};
