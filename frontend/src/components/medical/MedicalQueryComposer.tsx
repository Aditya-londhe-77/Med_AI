import React, { useState } from "react";
import { Search, Send, Sliders, Sparkles, AlertCircle, Stethoscope, Pill, BookOpen } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface PresetClinicalQuery {
  id: string;
  domain: string;
  title: string;
  query: string;
  icon?: React.ElementType;
}

export const PRESET_MEDICAL_QUERIES: PresetClinicalQuery[] = [
  {
    id: "med-1",
    domain: "DIABETES & BLOOD SUGAR",
    title: "Type 2 Diabetes First-Choice Medicines",
    query: "What is the recommended first-choice medicine for Type 2 diabetes according to standard health guidelines, and when should metformin not be taken?",
    icon: Pill,
  },
  {
    id: "med-2",
    domain: "HEART & BLOOD PRESSURE",
    title: "High Blood Pressure Medicines Comparison",
    query: "What are the common medical guidelines for managing high blood pressure, and how do ACE inhibitors compare with ARBs for kidney health?",
    icon: Stethoscope,
  },
  {
    id: "med-3",
    domain: "CHOLESTEROL MEDICINES",
    title: "Statin Medicines & Liver Checkups",
    query: "What is the medical evidence about whether statins cause liver problems, and do patients need routine liver blood tests while taking them?",
    icon: BookOpen,
  },
  {
    id: "med-4",
    domain: "LUNG HEALTH & BREATHING",
    title: "Asthma Inhalers & Stepping Up Care",
    query: "What do medical guidelines recommend when a standard low-dose steroid inhaler does not fully control asthma symptoms?",
    icon: Stethoscope,
  },
];

interface MedicalQueryComposerProps {
  onSubmit: (query: string, options: { includeMedication: boolean; includeClinical: boolean }) => void;
  isSubmitting?: boolean;
  errorMessage?: string;
  activeAgentsCount?: number;
  totalAgentsCount?: number;
}

export function MedicalQueryComposer({
  onSubmit,
  isSubmitting = false,
  errorMessage,
  activeAgentsCount,
  totalAgentsCount,
}: MedicalQueryComposerProps) {
  const [query, setQuery] = useState("");
  const [includeMedication, setIncludeMedication] = useState(true);
  const [includeClinical, setIncludeClinical] = useState(true);
  const [showOptions, setShowOptions] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSubmitting) return;
    onSubmit(query.trim(), {
      includeMedication,
      includeClinical,
    });
  };

  const handleSelectPreset = (preset: PresetClinicalQuery) => {
    setQuery(preset.query);
  };

  return (
    <div className="space-y-6">
      {/* Floating Search Container */}
      <div className="relative rounded-3xl bg-white/95 backdrop-blur-sm border border-pink-200/90 shadow-lg shadow-pink-500/5 p-4 sm:p-6 transition-all focus-within:shadow-xl focus-within:shadow-pink-500/10 focus-within:border-pink-300">
        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div className="relative flex items-center">
            <div className="absolute left-4 text-[#7652D6]">
              <Search className="w-5 h-5" />
            </div>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask any health or medicine question (e.g. 'What helps with high blood pressure?')..."
              className="h-14 sm:h-16 w-full rounded-full border-pink-200/80 bg-[#FFF5F9]/50 pl-12 pr-36 sm:pr-44 text-xs sm:text-sm md:text-base text-[#29243A] placeholder:text-[#777187]/70 focus-visible:ring-2 focus-visible:ring-pink-300/40"
            />
            <Button
              type="submit"
              disabled={!query.trim() || isSubmitting}
              className="absolute right-2 h-10 sm:h-12 px-4 sm:px-6 rounded-full bg-gradient-to-r from-[#7652D6] via-[#E879B9] to-[#F472B6] hover:opacity-95 text-white font-bold text-xs sm:text-sm shadow-md shadow-pink-500/20 transition-all active:scale-95 gap-1.5"
            >
              <span>{isSubmitting ? "Searching..." : "Ask AI"}</span>
              <Send className="w-3.5 h-3.5" />
            </Button>
          </div>

          {/* Error banner */}
          {errorMessage && (
            <div className="p-3 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2 animate-in fade-in">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
              <span className="font-medium">{errorMessage}</span>
            </div>
          )}

          {/* Sub-Bar: Functional agent counter and options toggle */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs text-[#777187]">
            {activeAgentsCount !== undefined ? (
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 font-semibold text-[#7652D6] bg-[#FFF0F5] border border-pink-200 rounded-full px-3 py-1 text-xs">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  {activeAgentsCount} of {totalAgentsCount || 6} Agents Selected
                </span>
              </div>
            ) : <div />}

            <button
              type="button"
              onClick={() => setShowOptions(!showOptions)}
              className="inline-flex items-center gap-1 text-[11px] sm:text-xs font-semibold text-[#7652D6] hover:text-[#4B2B91] py-1 px-2.5 rounded-full hover:bg-pink-50 transition-colors cursor-pointer"
            >
              <Sliders className="w-3 h-3" />
              <span>{showOptions ? "Fewer Options" : "More Options"}</span>
            </button>
          </div>

          {/* Options Dropdown */}
          {showOptions && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-pink-100 text-xs animate-in slide-in-from-top-2">
              <button
                type="button"
                onClick={() => setIncludeMedication(!includeMedication)}
                className={cn(
                  "py-2 px-3.5 rounded-full border text-left text-xs font-semibold transition-all flex items-center justify-between",
                  includeMedication
                    ? "bg-[#FFF0F5] border-pink-300 text-[#7652D6]"
                    : "bg-gray-50 border-gray-200 text-gray-500"
                )}
              >
                <span>Medicine & Dosage Details</span>
                <span className="font-bold">{includeMedication ? "✓ On" : "✕ Off"}</span>
              </button>

              <button
                type="button"
                onClick={() => setIncludeClinical(!includeClinical)}
                className={cn(
                  "py-2 px-3.5 rounded-full border text-left text-xs font-semibold transition-all flex items-center justify-between",
                  includeClinical
                    ? "bg-[#FFF0F5] border-pink-300 text-[#7652D6]"
                    : "bg-gray-50 border-gray-200 text-gray-500"
                )}
              >
                <span>Symptoms & Causes Details</span>
                <span className="font-bold">{includeClinical ? "✓ On" : "✕ Off"}</span>
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Suggested Questions: Clean, Softly Rounded Pills */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-[#777187] flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-pink-500" />
            Popular Health Questions
          </span>
          <span className="text-[11px] text-[#7652D6] font-medium">Tap any question to ask</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {PRESET_MEDICAL_QUERIES.map((preset) => {
            const Icon = preset.icon || Stethoscope;
            return (
              <div
                key={preset.id}
                onClick={() => handleSelectPreset(preset)}
                className="group cursor-pointer rounded-2xl border border-pink-200/70 bg-white/80 hover:bg-white p-3.5 hover:border-pink-300 hover:shadow-md hover:shadow-pink-500/5 transition-all space-y-1.5 select-none"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-[#FFF0F5] text-[#7652D6] flex items-center justify-center shrink-0 group-hover:bg-[#7652D6] group-hover:text-white transition-colors">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-bold text-[#29243A] group-hover:text-[#7652D6] transition-colors line-clamp-1">
                      {preset.title}
                    </span>
                  </div>
                  <span className="text-[10px] font-bold text-pink-500 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    Ask →
                  </span>
                </div>
                <p className="text-[11px] text-[#777187] line-clamp-2 leading-relaxed pl-9">
                  {preset.query}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
