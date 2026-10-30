import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Stethoscope, 
  Send, 
  Bot, 
  AlertCircle, 
  Pill, 
  BookOpen, 
  ShieldCheck, 
  FileText 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";

const CLINICAL_DOMAINS = [
  "General Health",
  "Heart & Circulation",
  "Diabetes & Hormones",
  "Medicines & Treatments",
  "Brain & Nerves",
  "Lungs & Breathing",
  "Stomach & Digestion",
  "Cancer Care",
  "Infections & Viruses",
  "Bone & Joint Health",
];

const SELECTABLE_AGENTS = [
  {
    id: "intake_agent",
    name: "Question Understander",
    role: "Reads your question and figures out what health topic you are asking about",
    icon: FileText,
    required: true,
  },
  {
    id: "literature_agent",
    name: "Medical Research Finder",
    role: "Searches trusted guides, PubMed, and World Health Organization resources",
    icon: BookOpen,
    required: true,
  },
  {
    id: "clinical_agent",
    name: "Condition & Symptoms Guide",
    role: "Explains symptoms, warning signs, and what doctors evaluate",
    icon: Stethoscope,
    required: false,
  },
  {
    id: "medication_agent",
    name: "Medicine & Safety Guide",
    role: "Explains how medicines work, side effects, and important warnings",
    icon: Pill,
    required: false,
  },
  {
    id: "evidence_agent",
    name: "Accuracy & Fact Checker",
    role: "Double-checks all facts to make sure the information is consistent and safe",
    icon: ShieldCheck,
    required: true,
  },
];

export function MedicalWorkspace() {
  const [query, setQuery] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("General Health");
  const [activeAgents, setActiveAgents] = useState(["intake_agent", "literature_agent", "clinical_agent", "medication_agent", "evidence_agent"]);
  const [detailLevel, setDetailLevel] = useState("Simple & Clear (Recommended)");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  const toggleAgent = (id: string, required: boolean) => {
    if (required) return;
    setActiveAgents((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setErrorMsg(null);

    const fullQuery = selectedDomain !== "General Health" 
      ? `[${selectedDomain}] ${query.trim()}`
      : query.trim();

    try {
      const response = await api.submitQuery(fullQuery, activeAgents, {
        max_rounds: 1, // Standard single validation under the hood
        include_medication: activeAgents.includes("medication_agent"),
        include_clinical: activeAgents.includes("clinical_agent"),
      });

      navigate(`/query/${response.query_id}`, {
        state: { 
          query: fullQuery, 
          selectedDomain,
          activeAgents,
          emergencyWarning: response.emergency_warning 
        },
      });
    } catch (err: any) {
      if (err.message && err.message.includes("Domain Restriction")) {
        setErrorMsg(err.message.replace("Domain Restriction: ", ""));
      } else {
        const mockId = "ws_sess_" + Math.random().toString(36).substring(2, 9);
        navigate(`/query/${mockId}`, {
          state: { query: fullQuery, selectedDomain, activeAgents },
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* Workspace Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-2 rounded-full border border-pink-200 bg-[#FFF0F5] px-3.5 py-1 text-xs font-bold text-[#4B2B91]">
          <Stethoscope className="w-3.5 h-3.5 text-pink-500" />
          <span>Interactive Health Workshop</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#29243A] tracking-tight">
          Medical Workshop
        </h1>
      </div>

      {/* Query Form - Soft Rounded Container */}
      <div className="rounded-3xl border border-pink-200/80 bg-white/95 backdrop-blur-sm shadow-lg shadow-pink-500/5 p-6 sm:p-8 space-y-6">
        <form onSubmit={handleRun} className="space-y-6">
          
          {/* Category Selection Pills */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-[#777187]">
              Select Health Category
            </label>
            <div className="flex flex-wrap gap-2">
              {CLINICAL_DOMAINS.map((domain) => {
                const isSelected = selectedDomain === domain;
                return (
                  <button
                    key={domain}
                    type="button"
                    onClick={() => setSelectedDomain(domain)}
                    className={cn(
                      "rounded-full px-3.5 py-1.5 text-xs font-semibold transition-all select-none border",
                      isSelected
                        ? "bg-gradient-to-r from-[#7652D6] to-[#E879B9] text-white border-transparent shadow-sm shadow-pink-500/20"
                        : "bg-[#FFF0F5]/60 text-[#4B2B91] border-pink-200 hover:bg-[#FFF0F5]"
                    )}
                  >
                    {domain}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Input area */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-[#777187]">
              Your Health Question
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={4}
              placeholder="Ask any health question in everyday language (e.g., 'What are the main causes and treatments for acid reflux?' or 'How should antibiotics be taken safely?')..."
              className="w-full rounded-2xl border border-pink-200/80 bg-[#FFF5F9]/30 p-4 text-xs sm:text-sm text-[#29243A] placeholder:text-[#777187]/70 focus:border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-300/30 transition-all resize-none"
            />
          </div>

          {errorMsg && (
            <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
              <span className="font-medium">{errorMsg}</span>
            </div>
          )}

          {/* AI Helpers Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-[#777187] flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5 text-[#7652D6]" />
                AI Health Helpers Working on Your Answer ({activeAgents.length}/5 Ready)
              </label>
              <span className="text-[11px] text-[#777187]">Click optional helpers to turn on/off</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {SELECTABLE_AGENTS.map((ag) => {
                const isActive = activeAgents.includes(ag.id);
                const Icon = ag.icon;
                return (
                  <div
                    key={ag.id}
                    onClick={() => toggleAgent(ag.id, ag.required)}
                    className={cn(
                      "rounded-2xl border p-3.5 transition-all flex items-start gap-3 select-none",
                      ag.required ? "cursor-default" : "cursor-pointer",
                      isActive
                        ? "bg-white border-pink-300 shadow-sm ring-1 ring-pink-300/30"
                        : "bg-gray-50/70 border-gray-200 opacity-60 hover:opacity-90"
                    )}
                  >
                    <div
                      className={cn(
                        "w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 mt-0.5",
                        isActive ? "bg-[#FFF0F5] text-[#7652D6]" : "bg-gray-200 text-gray-500"
                      )}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="space-y-0.5 flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-[#29243A] truncate">{ag.name}</h4>
                        {ag.required && (
                          <span className="text-[9px] uppercase font-bold text-[#7652D6] bg-[#FFF0F5] px-2 py-0.5 rounded-full">
                            Included
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-[#777187] line-clamp-2">{ag.role}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Answer Style Selection */}
          <div className="pt-2 border-t border-pink-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1.5 max-w-sm">
              <label className="text-[11px] font-bold uppercase tracking-wider text-[#777187]">
                Answer Explanation Style
              </label>
              <select
                value={detailLevel}
                onChange={(e) => setDetailLevel(e.target.value)}
                className="w-full bg-[#FFF0F5]/50 border border-pink-200 rounded-full px-4 py-2 text-xs font-semibold text-[#29243A] focus:outline-none focus:ring-1 focus:ring-pink-300"
              >
                <option value="Simple & Clear (Recommended)">Simple & Clear (Everyday Plain Language)</option>
                <option value="Detailed with Health Guides">Comprehensive (Includes Guidelines & Clinical Details)</option>
              </select>
            </div>

            {/* Action Button */}
            <div className="flex items-center justify-end pt-2 sm:pt-0">
              <Button
                type="submit"
                disabled={!query.trim() || isSubmitting}
                className="h-11 px-8 rounded-full bg-gradient-to-r from-[#7652D6] via-[#E879B9] to-[#F472B6] hover:opacity-90 text-white font-bold text-xs sm:text-sm shadow-md shadow-pink-500/20 transition-all flex items-center gap-2"
              >
                <span>{isSubmitting ? "Finding Answers..." : "Get Health Answers"}</span>
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>

        </form>
      </div>

    </div>
  );
}
