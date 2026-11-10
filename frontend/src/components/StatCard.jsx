import React from 'react';

const TIER_STYLES = {
  safe: {
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    dot: 'bg-emerald-400',
  },
  low: {
    border: 'border-sky-500/30',
    bg: 'bg-sky-500/10',
    text: 'text-sky-400',
    dot: 'bg-sky-400',
  },
  medium: {
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    dot: 'bg-amber-400',
  },
  high: {
    border: 'border-orange-500/30',
    bg: 'bg-orange-500/10',
    text: 'text-orange-400',
    dot: 'bg-orange-400',
  },
  critical: {
    border: 'border-red-500/40',
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    dot: 'bg-red-500',
  },
  neutral: {
    border: 'border-slate-800',
    bg: 'bg-slate-800/40',
    text: 'text-slate-300',
    dot: 'bg-slate-400',
  },
};

export default function StatCard({
  title,
  value,
  subtext,
  icon: Icon,
  variant = 'neutral',
  badge,
}) {
  const style = TIER_STYLES[variant.toLowerCase()] || TIER_STYLES.neutral;

  return (
    <div
      className={`bg-slate-900 border rounded-2xl p-4 shadow-xl flex flex-col justify-between transition hover:border-slate-700 ${style.border}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-xl ${style.bg} ${style.text}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between mt-1">
        <div className="text-2xl lg:text-3xl font-extrabold text-slate-100 font-mono tracking-tight">
          {value}
        </div>
        {badge && (
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
            {badge}
          </span>
        )}
      </div>

      {subtext && (
        <div className="mt-3 text-[11px] text-slate-400 flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
          <span className="truncate">{subtext}</span>
        </div>
      )}
    </div>
  );
}
