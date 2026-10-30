import { useState, useEffect } from "react";
import { 
  Bot, 
  Save, 
  Check, 
  Sliders, 
  Cpu
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api, type SystemConfig } from "@/services/api";

const MEDICAL_AGENTS_SPEC = [
  {
    id: "intake_agent",
    name: "Question Helper",
    role: "Reads your question, figures out the health category, and makes sure it is safe to answer.",
    model: "gemini-1.5-flash",
    tier: "Fast Assistant",
    tools: ["Question Reader", "Topic Categorizer", "Emergency Detector"],
  },
  {
    id: "literature_agent",
    name: "Research Helper",
    role: "Finds medical information from trusted health organizations including WHO, NIH, and CDC.",
    model: "gemini-1.5-flash",
    tier: "Fast Assistant",
    tools: ["Health Web Search", "Health Guidelines", "Trusted Fact Finder"],
  },
  {
    id: "clinical_agent",
    name: "Condition Guide",
    role: "Explains symptoms, common warning signs, and standard medical checkups in everyday language.",
    model: "gemini-1.5-flash",
    tier: "Fast Assistant",
    tools: ["Symptom Explainer", "Common Conditions", "Doctor Checkups"],
  },
  {
    id: "medication_agent",
    name: "Medicine Guide",
    role: "Explains how common medicines work, potential side effects, and important warnings.",
    model: "gemini-1.5-flash",
    tier: "Fast Assistant",
    tools: ["Approved Medicines", "Medicine Checks", "Safety Warnings"],
  },
  {
    id: "evidence_agent",
    name: "Fact Checker",
    role: "Double-checks all medical facts against authoritative guidelines to prevent mistakes.",
    model: "gemini-1.5-pro",
    tier: "Deep Fact-Checker",
    tools: ["Fact Checker", "Mistake Detector", "Reliability Grader"],
  },
  {
    id: "synthesis_agent",
    name: "Report Writer",
    role: "Puts all verified information together into a simple, easy-to-read summary anyone can understand.",
    model: "gemini-1.5-pro",
    tier: "Clear Writer",
    tools: ["Simple Summary", "Clear Language", "Key Points Finder"],
  },
  {
    id: "safety_guard_agent",
    name: "Patient Safety Helper",
    role: "Ensures safety warnings are clear and reminds users when they should consult a doctor.",
    model: "gemini-1.5-flash",
    tier: "Safety Helper",
    tools: ["Safety Checker", "Notice Attacher", "Emergency Helpline Link"],
  },
];

export function AgentConfig() {
  const [saved, setSaved] = useState(false);
  const [minGrade, setMinGrade] = useState("Grade B");
  const [, setSystemConfig] = useState<SystemConfig | null>(null);

  useEffect(() => {
    api.fetchSystemConfig().then((cfg) => setSystemConfig(cfg)).catch(() => {});
  }, []);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="border-b border-pink-200/80 pb-5 space-y-1.5">
        <div className="inline-flex items-center gap-2 rounded-full border border-pink-200 bg-[#FFF0F5] px-3.5 py-1 text-xs font-bold text-[#4B2B91]">
          <Bot className="w-3.5 h-3.5 text-pink-500" />
          <span>AI Health Helpers & System Preferences</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#29243A] tracking-tight">
          AI Health Helpers Overview
        </h1>
      </div>

      {/* Agent Cards Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#29243A] flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#7652D6]" />
            Your Dedicated AI Health Helpers (7 Helpers)
          </h2>
          <Badge className="bg-[#FFF0F5] text-[#4B2B91] border-pink-200 font-bold" variant="outline">
            Active & Coordinated
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {MEDICAL_AGENTS_SPEC.map((agent) => (
            <div key={agent.id} className="rounded-2xl border border-pink-200/70 bg-white/90 backdrop-blur-sm p-4 sm:p-5 space-y-3 shadow-xs hover:border-pink-300 hover:shadow-md hover:shadow-pink-500/5 transition-all">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="text-xs sm:text-sm font-bold text-[#29243A]">{agent.name}</h3>
                  <span className="text-[10px] text-pink-600 font-semibold">{agent.tier}</span>
                </div>
                <Badge
                  variant="outline"
                  className="bg-[#FFF0F5] text-[#7652D6] border-pink-200 text-[10px] font-medium rounded-full px-2.5 py-0.5"
                >
                  {agent.model.includes("pro") ? "Deep AI" : "Fast AI"}
                </Badge>
              </div>

              <p className="text-[11px] sm:text-xs text-[#777187] leading-relaxed">
                {agent.role}
              </p>

              <div className="pt-2 border-t border-pink-100/80 flex flex-wrap gap-1">
                {agent.tools.map((t) => (
                  <span
                    key={t}
                    className="px-2.5 py-0.5 rounded-full bg-[#FFF5F9] border border-pink-100 text-[9px] text-[#4B2B91] font-medium"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Preferences Section */}
      <div className="max-w-xl">
        <div className="rounded-3xl border border-pink-200/80 bg-white/95 backdrop-blur-sm shadow-xs overflow-hidden">
          <div className="py-4 px-6 border-b border-pink-100 bg-[#FFF5F9]">
            <h3 className="text-xs sm:text-sm font-bold text-[#29243A] flex items-center gap-2">
              <Sliders className="w-4 h-4 text-[#7652D6]" />
              Health Answer Preferences
            </h3>
          </div>
          <div className="p-6 space-y-4 text-xs">
            <div className="space-y-1.5">
              <label className="text-[11px] font-bold uppercase tracking-wider text-[#777187]">
                Information Detail Level
              </label>
              <select
                value={minGrade}
                onChange={(e) => setMinGrade(e.target.value)}
                className="w-full bg-[#FFF0F5]/50 border border-pink-200 rounded-full px-4 py-2 text-xs font-semibold text-[#29243A] focus:outline-none focus:ring-1 focus:ring-pink-300"
              >
                <option value="Grade B">Standard (Clinical Guidelines & Clear Overviews)</option>
                <option value="Grade A">High Precision Only (Official Medical Guidelines Only)</option>
                <option value="All">All Resources (Includes General Patient Handouts)</option>
              </select>
            </div>

            <div className="pt-2">
              <Button
                onClick={handleSave}
                className="h-10 px-6 rounded-full bg-gradient-to-r from-[#7652D6] to-[#E879B9] hover:opacity-90 text-white font-bold text-xs shadow-xs flex items-center gap-1.5"
              >
                {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
                <span>{saved ? "Preferences Saved!" : "Save Preferences"}</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
