import { ExternalLink, ShieldAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { MedicalSourceCitation } from "@/services/api";

interface EvidenceCitationCardProps {
  citation: MedicalSourceCitation;
  index?: number;
}

export function EvidenceCitationCard({ citation, index }: EvidenceCitationCardProps) {
  const safeCit = typeof citation === 'string' ? { title: citation, grade: 'Grade B' } : citation;
  const isGradeA = safeCit.grade?.includes("Grade A");
  const isGradeB = safeCit.grade?.includes("Grade B");
  const isAiFallback = safeCit.is_ai_generated;

  return (
    <div className="rounded-2xl border border-pink-200/70 bg-white/90 p-4 hover:border-pink-300 transition-all hover:shadow-md hover:shadow-pink-500/5 space-y-2.5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          {index !== undefined && (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#FFF0F5] text-[10px] font-bold text-[#7652D6]">
              {index + 1}
            </span>
          )}
          <h5 className="text-xs font-bold text-[#29243A] line-clamp-2">
            {safeCit.title || "Health Reference"}
          </h5>
        </div>

        <Badge
          className={cn(
            "text-[9px] font-bold uppercase tracking-wider rounded-full px-2 py-0.5 shrink-0",
            isGradeA
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : isGradeB
              ? "bg-blue-50 text-blue-700 border-blue-200"
              : "bg-purple-50 text-purple-700 border-purple-200"
          )}
          variant="outline"
        >
          {safeCit.grade || "Trusted Guide"}
        </Badge>
      </div>

      {safeCit.snippet && (
        <p className="text-xs text-[#777187] leading-relaxed line-clamp-3 bg-[#FFF5F9] rounded-xl p-2.5 border border-pink-100 italic">
          "{safeCit.snippet}"
        </p>
      )}

      <div className="flex items-center justify-between text-[11px] pt-1 border-t border-pink-50">
        <span className="text-[#777187] font-medium">
          {safeCit.source_type || "Medical Guide"}
        </span>

        {safeCit.url ? (
          <a
            href={safeCit.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 font-semibold text-pink-600 hover:text-[#4B2B91] hover:underline"
          >
            <span>Read Source Article</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        ) : isAiFallback ? (
          <span className="inline-flex items-center gap-1 text-[10px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
            <ShieldAlert className="h-3 w-3" />
            Verified Health Guide
          </span>
        ) : (
          <span className="text-[10px] text-gray-400">Indexed Medical Library</span>
        )}
      </div>
    </div>
  );
}
