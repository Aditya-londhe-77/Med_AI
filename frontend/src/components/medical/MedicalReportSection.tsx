import { BookOpen, Stethoscope, Pill, ShieldCheck, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { MedicalReportSection as SectionType } from "@/services/api";

interface MedicalReportSectionProps {
  section: SectionType;
}

const SECTION_ICONS: Record<string, React.ElementType> = {
  overview: BookOpen,
  clinical_info: Stethoscope,
  medication: Pill,
  evidence: ShieldCheck,
  safety: AlertCircle,
};

export function MedicalReportSection({ section }: MedicalReportSectionProps) {
  const Icon = SECTION_ICONS[section.section_type] || BookOpen;
  const isSafety = section.section_type === "safety";

  return (
    <div
      className={cn(
        "rounded-2xl border p-5 md:p-6 transition-all bg-white shadow-xs",
        isSafety
          ? "border-amber-200 bg-amber-50/20"
          : "border-pink-200/90 hover:border-pink-300"
      )}
    >
      <div className="flex items-center gap-3 mb-3">
        <div
          className={cn(
            "w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-xs",
            isSafety
              ? "bg-amber-100 text-amber-700"
              : "bg-[#FFF0F5] text-[#7652D6]"
          )}
        >
          <Icon className="w-4 h-4" />
        </div>
        <h4 className="text-base font-bold text-[#29243A] tracking-tight">
          {section.title}
        </h4>
      </div>

      <div className="text-xs md:text-sm text-[#29243A]/90 leading-relaxed space-y-2 whitespace-pre-line pl-1">
        {typeof section.content === 'string' ? section.content : JSON.stringify(section.content || '')}
      </div>
    </div>
  );
}
