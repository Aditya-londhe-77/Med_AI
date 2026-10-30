import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  /** Score between 0 and 100 */
  score: number;
  /** Optional extra class names */
  className?: string;
  /** Show the numeric score next to the label */
  showScore?: boolean;
}

/**
 * ConfidenceBadge — displays a colour-coded confidence level.
 *
 * Thresholds:
 *   ≥ 80  → green  (HIGH)
 *   ≥ 55  → yellow (MEDIUM)
 *   < 55  → red    (LOW)
 */
export function ConfidenceBadge({ score, className, showScore = true }: ConfidenceBadgeProps) {
  const level =
    score >= 80 ? "high" : score >= 55 ? "medium" : "low";

  const styles = {
    high: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    low: "bg-red-500/15 text-red-400 border-red-500/30",
  };

  const labels = { high: "HIGH", medium: "MED", low: "LOW" };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold tracking-wider uppercase select-none",
        styles[level],
        className
      )}
      title={`Confidence: ${score}%`}
    >
      {/* Dot indicator */}
      <span className={cn("h-1.5 w-1.5 rounded-full", {
        "bg-emerald-400": level === "high",
        "bg-yellow-400": level === "medium",
        "bg-red-400":    level === "low",
      })} />
      {labels[level]}
      {showScore && <span className="opacity-70">· {score}%</span>}
    </span>
  );
}
