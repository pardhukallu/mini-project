import React from 'react';
import { Shield, ShieldAlert, ShieldCheck } from 'lucide-react';

interface SecurityScoreGaugeProps {
  score: number;
  deductions: number;
  assessed?: boolean;
}

export const SecurityScoreGauge: React.FC<SecurityScoreGaugeProps> = ({
  score,
  deductions,
  assessed = true,
}) => {
  // A score is not a clean bill of health until at least one live/local audit is recorded.
  let statusText = assessed ? 'EXCELLENT' : 'NOT ASSESSED';
  let statusColor = assessed ? 'text-emerald-400' : 'text-slate-400';
  let ringStroke = assessed ? '#10b981' : '#475569';
  let Icon = assessed ? ShieldCheck : Shield;

  if (assessed && score < 40) {
    statusText = 'CRITICAL EXPOSURE';
    statusColor = 'text-rose-400';
    ringStroke = '#f43f5e';
    Icon = ShieldAlert;
  } else if (assessed && score < 70) {
    statusText = 'ELEVATED RISK';
    statusColor = 'text-amber-400';
    ringStroke = '#f59e0b';
    Icon = ShieldAlert;
  } else if (assessed && score < 90) {
    statusText = 'MODERATE';
    statusColor = 'text-teal-400';
    ringStroke = '#14b8a6';
    Icon = Shield;
  }

  // SVG circular geometry
  const radius = 64;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - ((assessed ? score : 0) / 100) * circumference;

  return (
    <div className="bg-navy-850 border border-navy-700/80 rounded-lg p-6 flex flex-col items-center justify-between">
      <div className="w-full flex items-center justify-between border-b border-navy-800 pb-3 mb-4">
        <span className="text-xs font-mono font-medium uppercase tracking-wider text-slate-400">
          Privacy Posture Score
        </span>
        <span className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded border border-navy-700 bg-navy-900 ${statusColor}`}>
          {statusText}
        </span>
      </div>

      <div className="relative flex items-center justify-center my-2">
        <svg height={radius * 2} width={radius * 2} className="rotate-[-90deg]">
          {/* Background circle */}
          <circle
            stroke="#1e293b"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Foreground progress circle */}
          <circle
            stroke={ringStroke}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease-in-out' }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center text-center">
          <Icon className={`w-5 h-5 mb-0.5 ${statusColor}`} />
          <span className="text-3xl font-extrabold font-mono text-slate-100 tracking-tight">
            {assessed ? score : '—'}
          </span>
          <span className="text-[10px] font-mono text-slate-400">/ 100</span>
        </div>
      </div>

      <div className="w-full mt-4 pt-3 border-t border-navy-800/80 text-xs font-mono text-slate-400 flex items-center justify-between">
        <span>Active Deductions:</span>
        <span className={deductions > 0 ? 'text-rose-400 font-semibold' : 'text-emerald-400 font-semibold'}>
          {!assessed ? 'Complete an audit to establish a baseline' : deductions > 0 ? `-${deductions} pts` : '0 pts (No known risk deductions)'}
        </span>
      </div>
    </div>
  );
};
