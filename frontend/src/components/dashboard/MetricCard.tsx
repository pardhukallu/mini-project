import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: LucideIcon;
  variant?: 'clean' | 'warning' | 'critical' | 'neutral';
  badgeText?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'neutral',
  badgeText,
}) => {
  const variantStyles = {
    clean: {
      border: 'border-emerald-500/30',
      bg: 'bg-emerald-500/5',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      icon: 'text-emerald-400',
    },
    warning: {
      border: 'border-amber-500/30',
      bg: 'bg-amber-500/5',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      icon: 'text-amber-400',
    },
    critical: {
      border: 'border-rose-500/30',
      bg: 'bg-rose-500/5',
      badge: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      icon: 'text-rose-400',
    },
    neutral: {
      border: 'border-navy-700/80',
      bg: 'bg-navy-850',
      badge: 'bg-navy-800 text-teal-400 border-navy-700',
      icon: 'text-teal-400',
    },
  }[variant];

  return (
    <div
      className={`rounded-lg border ${variantStyles.border} ${variantStyles.bg} p-5 flex flex-col justify-between transition duration-150`}
    >
      <div className="flex items-start justify-between">
        <span className="text-[11px] font-mono font-medium uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className="p-2 rounded bg-navy-900 border border-navy-800">
          <Icon className={`w-4 h-4 ${variantStyles.icon}`} />
        </div>
      </div>

      <div className="mt-4">
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {value}
        </div>
        <div className="flex items-center justify-between mt-1.5">
          <span className="text-xs text-slate-400">{subtitle}</span>
          {badgeText && (
            <span
              className={`text-[10px] font-mono px-2 py-0.5 rounded border ${variantStyles.badge}`}
            >
              {badgeText}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
