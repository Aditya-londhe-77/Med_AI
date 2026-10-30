import { CheckCircle2, Clock, Sparkles, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface TimelineStep {
  id: string;
  label: string;
  description: string;
  status: "pending" | "running" | "completed" | "error";
  time?: string;
}

interface AgentWorkflowTimelineProps {
  steps: TimelineStep[];
  currentProgress?: number;
}

export function AgentWorkflowTimeline({
  steps,
  currentProgress = 0,
}: AgentWorkflowTimelineProps) {
  return (
    <div className="rounded-3xl border border-pink-200/80 bg-white/95 backdrop-blur-sm p-5 md:p-6 shadow-md">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-bold text-[#29243A] tracking-tight flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-pink-500" />
            AI Health Progress Steps
          </h3>
          <p className="text-xs text-[#777187] mt-0.5">
            How our AI helpers research, double-check, and explain your question
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-[#7652D6] bg-[#FFF0F5] px-2.5 py-1 rounded-full border border-pink-200">
            {Math.round(currentProgress)}% Done
          </span>
        </div>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-pink-100">
        {steps.map((step) => {
          const isCompleted = step.status === "completed";
          const isRunning = step.status === "running";
          const isError = step.status === "error";

          return (
            <div key={step.id} className="relative flex items-start gap-4 text-left">
              {/* Timeline Icon */}
              <div
                className={cn(
                  "absolute -left-6 flex h-6 w-6 items-center justify-center rounded-full border bg-white transition-all shadow-sm",
                  isCompleted && "border-[#7652D6] bg-[#7652D6] text-white",
                  isRunning && "border-[#E879B9] bg-[#FFF1F7] text-[#E879B9] ring-4 ring-[#E879B9]/20 animate-pulse",
                  isError && "border-red-500 bg-red-100 text-red-600",
                  !isCompleted && !isRunning && !isError && "border-gray-200 text-gray-300"
                )}
              >
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : isRunning ? (
                  <div className="h-2 w-2 rounded-full bg-[#E879B9] animate-ping" />
                ) : isError ? (
                  <AlertCircle className="h-4 w-4" />
                ) : (
                  <Clock className="h-3 w-3" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 space-y-0.5">
                <div className="flex items-center justify-between">
                  <span
                    className={cn(
                      "text-sm font-bold tracking-tight transition-colors",
                      isCompleted && "text-[#29243A]",
                      isRunning && "text-[#7652D6]",
                      isError && "text-red-700",
                      !isCompleted && !isRunning && !isError && "text-[#777187]/70"
                    )}
                  >
                    {step.label}
                  </span>
                  {step.time && (
                    <span className="font-mono text-[10px] text-[#777187] bg-gray-50 px-1.5 py-0.5 rounded">
                      {step.time}
                    </span>
                  )}
                </div>
                <p className="text-xs text-[#777187] leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
