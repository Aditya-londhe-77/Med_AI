import React from "react";
import { Stethoscope, ArrowRight } from "lucide-react";
import { Button } from "./button";

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export function EmptyState({
  title = "No medical research found",
  description = "Submit a medical question or explore clinical topics using the workspace.",
  actionLabel,
  onAction,
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center border border-dashed border-[#E9E2F2] rounded-3xl bg-white/60 backdrop-blur-sm">
      <div className="w-14 h-14 rounded-2xl bg-[#F3EEFF] text-[#7652D6] flex items-center justify-center mb-4 shadow-sm">
        {icon || <Stethoscope className="w-7 h-7" />}
      </div>
      <h3 className="text-base font-bold text-[#29243A] tracking-tight">{title}</h3>
      <p className="mt-1.5 max-w-sm text-xs md:text-sm text-[#777187] leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button
          onClick={onAction}
          className="mt-5 h-9 px-4 text-xs font-semibold rounded-xl bg-[#7652D6] hover:bg-[#4B2B91] text-white shadow-sm shadow-[#7652D6]/20 flex items-center gap-2"
        >
          <span>{actionLabel}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Button>
      )}
    </div>
  );
}
