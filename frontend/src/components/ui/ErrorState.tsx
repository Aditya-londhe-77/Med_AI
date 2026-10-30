import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "./button";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Research Pipeline Error",
  message = "An error occurred while communicating with the medical intelligence orchestrator.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center border border-red-200 bg-red-50/50 rounded-3xl">
      <div className="w-12 h-12 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center mb-3">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h3 className="text-base font-bold text-red-950 tracking-tight">{title}</h3>
      <p className="mt-1 max-w-md text-xs md:text-sm text-red-800 leading-relaxed font-mono">
        {message}
      </p>
      {onRetry && (
        <Button
          onClick={onRetry}
          variant="outline"
          className="mt-4 h-9 px-4 text-xs font-semibold rounded-xl border-red-200 text-red-700 hover:bg-red-100/60 flex items-center gap-2"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Try Again</span>
        </Button>
      )}
    </div>
  );
}
