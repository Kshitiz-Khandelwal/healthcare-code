import { generateEcgWave } from "@/lib/mock-data";

export function EcgWave({ height = 80, hr = 80, animated = true }: { height?: number; hr?: number; animated?: boolean }) {
  const data = generateEcgWave(220, hr);
  const w = 600;
  const h = height;
  const path = data
    .map((p, i) => {
      const x = (i / (data.length - 1)) * w;
      const y = h / 2 - p.y * (h / 2.5);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" preserveAspectRatio="none" style={{ height }}>
      <defs>
        <pattern id="ecg-grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="0.4" className="text-border" />
        </pattern>
      </defs>
      <rect width={w} height={h} fill="url(#ecg-grid)" />
      <path d={path} className={`ecg-line ${animated ? "animate-ecg-draw" : ""}`} />
    </svg>
  );
}