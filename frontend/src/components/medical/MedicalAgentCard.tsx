import React from "react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { 
  FileText, 
  BookOpen, 
  Stethoscope, 
  Pill, 
  ShieldCheck, 
  Sparkles, 
  Lock 
} from "lucide-react";

export interface MedicalAgentProps {
  id: string;
  name: string;
  role: string;
  model: string;
  tools: string[];
  status?: "active" | "idle" | "running";
  onClick?: () => void;
  onToggle?: (id: string) => void;
  selected?: boolean;
  selectable?: boolean;
  required?: boolean;
}

const AGENT_ICONS: Record<string, React.ElementType> = {
  intake_agent: FileText,
  literature_agent: BookOpen,
  clinical_agent: Stethoscope,
  medication_agent: Pill,
  evidence_agent: ShieldCheck,
  synthesis_agent: Sparkles,
  safety_guard_agent: Lock,
};

export function MedicalAgentCard({
  id,
  name,
  role,
  model,
  tools,
  status = "idle",
  onClick,
  onToggle,
  selected = true,
  selectable = false,
}: MedicalAgentProps) {
  const Icon = AGENT_ICONS[id] || Stethoscope;
  const isRunning = status === "running";

  const handleClick = (e: React.MouseEvent) => {
    if (selectable && onToggle) {
      e.stopPropagation();
      onToggle(id);
    } else if (onClick) {
      onClick();
    }
  };

  return (
    <div
      onClick={handleClick}
      role={selectable ? "checkbox" : undefined}
      aria-checked={selectable ? selected : undefined}
      className={cn(
        "rounded-2xl border p-4 transition-all duration-200 relative overflow-hidden select-none",
        selectable || onClick ? "cursor-pointer" : "cursor-default",
        selected
          ? "border-pink-300/90 bg-white shadow-md shadow-pink-500/5 ring-1 ring-pink-300/30"
          : "border-gray-200/90 bg-gray-50/70 opacity-60 hover:opacity-90 hover:border-gray-300",
        isRunning && "border-pink-300 ring-2 ring-pink-300/40 animate-pulse"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "w-10 h-10 rounded-2xl flex items-center justify-center transition-all shadow-xs",
              selected
                ? "bg-gradient-to-tr from-[#7652D6] via-[#E879B9] to-[#F472B6] text-white shadow-pink-500/20"
                : "bg-gray-200 text-gray-400"
            )}
          >
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h4 className={cn("text-xs sm:text-sm font-bold tracking-tight", selected ? "text-[#29243A]" : "text-gray-600 line-through decoration-gray-400/50 decoration-1")}>
                {name}
              </h4>
            </div>
            <p className={cn("text-[11px] line-clamp-1", selected ? "text-[#777187]" : "text-gray-400")}>
              {role}
            </p>
          </div>
        </div>

        {/* Toggle Switch or Status Badge */}
        {selectable ? (
          <div className="flex items-center gap-2 shrink-0">
            <span
              className={cn(
                "text-[10px] font-bold px-2 py-0.5 rounded-full border transition-all",
                selected
                  ? "bg-[#FFF0F5] text-[#7652D6] border-pink-200"
                  : "bg-gray-100 text-gray-500 border-gray-200"
              )}
            >
              {selected ? "In Use" : "Excluded"}
            </span>
            {/* iOS style toggle switch */}
            <div
              className={cn(
                "w-9 h-5 rounded-full p-0.5 transition-colors relative flex items-center",
                selected
                  ? "bg-gradient-to-r from-[#7652D6] to-[#E879B9]"
                  : "bg-gray-300"
              )}
            >
              <div
                className={cn(
                  "w-4 h-4 rounded-full bg-white shadow-xs transition-transform transform",
                  selected ? "translate-x-4" : "translate-x-0"
                )}
              />
            </div>
          </div>
        ) : (
          <Badge
            variant="outline"
            className={cn(
              "text-[9px] font-semibold uppercase tracking-wider rounded-full px-2.5 py-0.5 shrink-0",
              isRunning
                ? "bg-[#FFF0F5] text-pink-600 border-pink-300 animate-pulse"
                : selected
                ? "bg-[#FFF0F5] text-[#7652D6] border-pink-300"
                : "bg-gray-100 text-gray-500 border-gray-200"
            )}
          >
            {status === "running" ? "Working" : selected ? "Active" : "Ready"}
          </Badge>
        )}
      </div>

      <div className={cn(
        "mt-3 pt-2.5 border-t flex items-center justify-between text-[11px]",
        selected ? "border-pink-100/80 text-[#777187]" : "border-gray-200 text-gray-400"
      )}>
        <div className={cn(
          "flex items-center gap-1.5 text-[10px] font-medium px-2.5 py-0.5 rounded-full",
          selected ? "text-[#7652D6] bg-[#FFF0F5]" : "text-gray-400 bg-gray-100"
        )}>
          <span>{model.includes("pro") ? "Deep Check" : "Fast Check"}</span>
        </div>
        <div className="flex flex-wrap gap-1 justify-end max-w-[65%]">
          {tools.slice(0, 2).map((tool) => (
            <span
              key={tool}
              className={cn(
                "px-2 py-0.5 rounded-full border text-[9px] font-medium truncate max-w-[100px]",
                selected
                  ? "bg-[#FFF5F9] border-pink-200/60 text-[#7652D6]"
                  : "bg-gray-100 border-gray-200 text-gray-400"
              )}
            >
              {tool}
            </span>
          ))}
          {tools.length > 2 && (
            <span className="text-[9px] font-medium self-center text-gray-400">
              +{tools.length - 2}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
