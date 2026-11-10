import React from 'react';

export default function Sparkline({
  data = [],
  color = '#38bdf8',
  height = 36,
  width = 120,
  strokeWidth = 2,
}) {
  if (!data || data.length < 2) {
    return (
      <div
        style={{ height, width }}
        className="flex items-center justify-center text-[10px] text-slate-500 font-mono"
      >
        --
      </div>
    );
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min === 0 ? 1 : max - min;
  const padding = 4;

  const points = data
    .map((val, index) => {
      const x = padding + (index / (data.length - 1)) * (width - padding * 2);
      const y = height - padding - ((val - min) / range) * (height - padding * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}
