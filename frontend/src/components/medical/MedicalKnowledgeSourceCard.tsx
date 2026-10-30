import { ExternalLink, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export interface KnowledgeSource {
  id: string;
  name: string;
  category: "Global Health" | "Clinical Research" | "Regulatory Agency" | "Systematic Reviews";
  evidenceGrade: "Grade A" | "Grade B";
  description: string;
  url: string;
  recordCount?: string;
}

interface MedicalKnowledgeSourceCardProps {
  source: KnowledgeSource;
}

export function MedicalKnowledgeSourceCard({ source }: MedicalKnowledgeSourceCardProps) {
  return (
    <div className="rounded-2xl border border-pink-200/70 bg-white/90 backdrop-blur-sm p-4 hover:border-pink-300 hover:shadow-md hover:shadow-pink-500/5 transition-all space-y-3 flex flex-col justify-between">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Badge
            variant="outline"
            className="text-[9px] font-bold text-[#7652D6] bg-[#FFF0F5] border-pink-200 rounded-full px-2 py-0.5"
          >
            {source.category}
          </Badge>
          <Badge
            className="text-[9px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border-emerald-200 rounded-full px-2 py-0.5"
            variant="outline"
          >
            {source.evidenceGrade}
          </Badge>
        </div>

        <h4 className="text-xs sm:text-sm font-bold text-[#29243A] tracking-tight">{source.name}</h4>
        <p className="text-[11px] text-[#777187] leading-relaxed line-clamp-2">
          {source.description}
        </p>
      </div>

      <div className="pt-2.5 border-t border-pink-100/80 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 text-emerald-600 font-semibold text-[11px]">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Verified</span>
        </div>
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-pink-600 hover:text-[#4B2B91] font-semibold text-[11px] hover:underline"
        >
          <span>Official Site</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
}
