import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { CheckCircle2, Shield } from 'lucide-react';

interface ExposureBreakdownChartProps {
  penalties: {
    email_breaches: number;
    footprint: number;
    domain_security: number;
    browser_permissions: number;
  };
}

export const ExposureBreakdownChart: React.FC<ExposureBreakdownChartProps> = ({
  penalties,
}) => {
  const chartData = [
    {
      category: 'Email Breaches',
      penalty: penalties.email_breaches,
      color: '#ef4444',
    },
    {
      category: 'OSINT Footprint',
      penalty: penalties.footprint,
      color: '#f5a623',
    },
    {
      category: 'Domain Email Security',
      penalty: penalties.domain_security,
      color: '#7c9cff',
    },
    {
      category: 'Browser Permissions',
      penalty: penalties.browser_permissions,
      color: '#4f8cff',
    },
  ];

  const totalPenalties =
    penalties.email_breaches +
    penalties.footprint +
    penalties.domain_security +
    penalties.browser_permissions;

  return (
    <div className="bg-navy-850 border border-navy-700/80 rounded-lg p-6 flex flex-col justify-between">
      <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-4">
        <div>
          <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-slate-300">
            Risk Vector Distribution
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Breakdown of point deductions calculated from active audit findings
          </p>
        </div>
        <div className="flex items-center space-x-1.5 text-xs font-mono text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded border border-teal-500/20">
          <Shield className="w-3.5 h-3.5" />
          <span>EVALUATION MODEL v1</span>
        </div>
      </div>

      {totalPenalties === 0 ? (
        <div className="h-44 flex flex-col items-center justify-center text-center p-4 rounded bg-navy-900/50 border border-dashed border-navy-800 my-auto">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mb-2" />
          <span className="text-sm font-mono font-medium text-slate-200">
            Clean Baseline Status
          </span>
          <p className="text-xs text-slate-400 max-w-sm mt-1">
            No verified risk deductions are currently recorded. Run the available audits to build an evidence-based assessment.
          </p>
        </div>
      ) : (
        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <XAxis
                type="number"
                domain={[0, 'auto']}
                tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
                axisLine={{ stroke: '#334155' }}
                tickLine={{ stroke: '#334155' }}
              />
              <YAxis
                dataKey="category"
                type="category"
                tick={{ fill: '#cbd5e1', fontSize: 11, fontFamily: 'monospace' }}
                axisLine={{ stroke: '#334155' }}
                tickLine={false}
                width={130}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '4px',
                  fontFamily: 'monospace',
                  fontSize: '11px',
                  color: '#f8fafc',
                }}
                formatter={(val: unknown) => [`-${val ?? 0} pts deduction`, 'Impact']}
              />
              <Bar dataKey="penalty" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-navy-800 text-[11px] font-mono text-slate-400 flex items-center justify-between">
        <span>Scoring formula: Base 100 - Σ(Active Vector Deductions)</span>
        <span className="text-teal-400">Strict Evidence-Based</span>
      </div>
    </div>
  );
};
