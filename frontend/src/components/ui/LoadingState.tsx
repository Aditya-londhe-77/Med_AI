import { Loader2, Sparkles } from "lucide-react";

interface LoadingStateProps {
  message?: string;
  subtext?: string;
}

export function LoadingState({
  message = "Analyzing medical evidence...",
  subtext = "Coordinating multi-agent research across clinical guidelines and pharmacology databases",
}: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center animate-in fade-in duration-500">
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#7652D6]/20 to-[#E879B9]/30 flex items-center justify-center text-[#7652D6] animate-pulse">
          <Loader2 className="w-8 h-8 animate-spin text-[#7652D6]" />
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-[#E879B9] text-white flex items-center justify-center shadow-md">
          <Sparkles className="w-3.5 h-3.5" />
        </div>
      </div>
      <h3 className="text-lg font-bold text-[#29243A] tracking-tight">{message}</h3>
      {subtext && (
        <p className="mt-2 max-w-md text-sm text-[#777187] leading-relaxed">
          {subtext}
        </p>
      )}
    </div>
  );
}
