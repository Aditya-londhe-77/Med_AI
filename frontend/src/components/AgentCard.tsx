import { CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type AgentStatus = "idle" | "running" | "done" | "error";

interface AgentCardProps {
  /** Display name of the agent */
  name: string;
  /** Short description / last logged action */
  description?: string;
  /** Current status */
  status?: AgentStatus;
  /** 0-100 progress value; only shown when status is 'running' */
  progress?: number;
}

/**
 * AgentCard — a compact card that shows an individual agent's status
 * during a live AEGIS query execution session.
 */
export function AgentCard({
  name,
  description,
  status = "idle",
  progress = 0,
}: AgentCardProps) {
  const statusStyles: Record<AgentStatus, string> = {
    idle:    "border-border/40  bg-card/30",
    running: "border-primary/40 bg-primary/5 shadow-[0_0_12px_0_hsl(var(--primary)/0.15)]",
    done:    "border-emerald-500/30 bg-emerald-500/5",
    error:   "border-red-500/30 bg-red-500/5",
  };

  const StatusIcon = () => {
    switch (status) {
      case "running":
        return <Loader2 className="w-4 h-4 text-primary animate-spin" />;
      case "done":
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />;
    }
  };

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-xl border px-4 py-3 transition-all duration-300",
        statusStyles[status]
      )}
    >
      <StatusIcon />
      <div className="flex-1 min-w-0">
        <p className={cn("text-sm font-semibold truncate", {
          "text-primary":          status === "running",
          "text-emerald-400":      status === "done",
          "text-red-400":          status === "error",
          "text-muted-foreground": status === "idle",
        })}>
          {name}
        </p>
        {description && (
          <p className="text-xs text-muted-foreground truncate mt-0.5">{description}</p>
        )}
        {status === "running" && (
          <div className="mt-2 h-1 w-full rounded-full bg-primary/20 overflow-hidden">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{ width: `${Math.max(5, progress)}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
