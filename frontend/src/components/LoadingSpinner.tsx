import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  /** Size in px — defaults to 40 */
  size?: number;
  /** Optional label rendered below the spinner */
  label?: string;
  /** Extra Tailwind classes applied to the wrapper */
  className?: string;
}

/**
 * LoadingSpinner — AEGIS branded spinner.
 *
 * Renders a dual-ring animated SVG with a pulsing shield icon in the centre,
 * matching the project's dark-mode glassmorphism aesthetic.
 */
export function LoadingSpinner({ size = 40, label, className }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      <div className="relative" style={{ width: size, height: size }}>
        {/* Outer ring */}
        <svg
          className="absolute inset-0 animate-spin"
          viewBox="0 0 50 50"
          width={size}
          height={size}
        >
          <circle
            cx="25"
            cy="25"
            r="20"
            fill="none"
            stroke="hsl(var(--primary))"
            strokeWidth="3"
            strokeDasharray="90 30"
            strokeLinecap="round"
          />
        </svg>

        {/* Inner ring — counter-spin for depth */}
        <svg
          className="absolute inset-0 animate-[spin_1.5s_linear_infinite_reverse]"
          viewBox="0 0 50 50"
          width={size}
          height={size}
        >
          <circle
            cx="25"
            cy="25"
            r="13"
            fill="none"
            stroke="hsl(var(--primary)/0.35)"
            strokeWidth="2"
            strokeDasharray="50 20"
            strokeLinecap="round"
          />
        </svg>

        {/* Centre dot */}
        <div
          className="absolute inset-0 flex items-center justify-center"
        >
          <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
        </div>
      </div>

      {label && (
        <p className="text-xs text-muted-foreground font-medium tracking-widest uppercase">
          {label}
        </p>
      )}
    </div>
  );
}
