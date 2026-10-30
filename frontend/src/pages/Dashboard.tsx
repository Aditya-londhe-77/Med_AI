import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Bot, 
  CheckCheck, 
  RotateCcw
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MedicalQueryComposer } from "@/components/medical/MedicalQueryComposer";
import { MedicalAgentCard, type MedicalAgentProps } from "@/components/medical/MedicalAgentCard";
import { api } from "@/services/api";

const CORE_MEDICAL_AGENTS: MedicalAgentProps[] = [
  {
    id: "literature_agent",
    name: "Medical Research Finder",
    role: "Looks up facts from trusted medical books, WHO, and official health guides",
    model: "gemini-1.5-flash",
    tools: ["Health Web Search", "Health Guidelines", "Trusted Fact Finder"],
    status: "idle",
  },
  {
    id: "clinical_agent",
    name: "Condition & Symptoms Guide",
    role: "Explains symptoms, what they mean, and what tests doctors usually do",
    model: "gemini-1.5-flash",
    tools: ["Symptom Explainer", "Common Conditions", "Doctor Checkups"],
    status: "idle",
  },
  {
    id: "medication_agent",
    name: "Medicine & Safety Guide",
    role: "Explains common medicines, how they work, and important precautions",
    model: "gemini-1.5-flash",
    tools: ["Approved Medicines", "Medicine Checks", "Safety Warnings"],
    status: "idle",
  },
  {
    id: "evidence_agent",
    name: "Accuracy & Fact Checker",
    role: "Double-checks all health facts to make sure they are accurate and consistent",
    model: "gemini-1.5-pro",
    tools: ["Fact Checker", "Mistake Detector", "Reliability Grader"],
    status: "idle",
  },
  {
    id: "synthesis_agent",
    name: "Easy Health Report Writer",
    role: "Puts all facts together into a clear, simple summary anyone can read",
    model: "gemini-1.5-pro",
    tools: ["Simple Summary", "Clear Language"],
    status: "idle",
  },
  {
    id: "intake_agent",
    name: "Question Understander",
    role: "Reads your question and figures out what health topic you need help with",
    model: "gemini-1.5-flash",
    tools: ["Question Reader", "Health Category Finder", "Safety Filter"],
    status: "idle",
  },
];

const DEFAULT_AGENTS = [
  "literature_agent",
  "clinical_agent",
  "medication_agent",
  "evidence_agent",
  "synthesis_agent",
  "intake_agent"
];

export function Dashboard() {
  const [selectedAgents, setSelectedAgents] = useState<string[]>(DEFAULT_AGENTS);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const toggleAgent = (id: string) => {
    setSelectedAgents((prev) => {
      if (prev.includes(id)) {
        if (prev.length === 1) {
          // Keep at least one agent active
          return prev;
        }
        return prev.filter((a) => a !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  const handleSelectAll = () => {
    setSelectedAgents(CORE_MEDICAL_AGENTS.map((a) => a.id));
  };

  const handleResetDefault = () => {
    setSelectedAgents(DEFAULT_AGENTS);
  };

  const handleRunQuery = async (
    query: string,
    options: { includeMedication: boolean; includeClinical: boolean }
  ) => {
    if (selectedAgents.length === 0) {
      setErrorMessage("Please select at least one AI agent to answer your question.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    const queryOptions = {
      includeMedication: selectedAgents.includes("medication_agent") && options.includeMedication,
      includeClinical: selectedAgents.includes("clinical_agent") && options.includeClinical,
      selected_agents: selectedAgents,
    };

    try {
      const response = await api.submitQuery(query, selectedAgents, {
        max_rounds: 1,
        include_medication: queryOptions.includeMedication,
        include_clinical: queryOptions.includeClinical,
      });

      navigate(`/query/${response.query_id}`, {
        state: { 
          query, 
          options: queryOptions, 
          selectedAgents, 
          emergencyWarning: response.emergency_warning 
        },
      });
    } catch (err: any) {
      console.error("Submission failed:", err);
      if (err.message && err.message.includes("Domain Restriction")) {
        setErrorMessage(err.message.replace("Domain Restriction: ", ""));
      } else {
        // Fallback for offline demo session
        const mockId = "med_sess_" + Math.random().toString(36).substring(2, 9);
        navigate(`/query/${mockId}`, {
          state: { query, options: queryOptions, selectedAgents },
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* Main Medical Query Composer */}
      <MedicalQueryComposer
        onSubmit={handleRunQuery}
        isSubmitting={isSubmitting}
        errorMessage={errorMessage || undefined}
        activeAgentsCount={selectedAgents.length}
        totalAgentsCount={CORE_MEDICAL_AGENTS.length}
      />

      {/* Interactive AI Agent Selector on Homepage */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-[#FFF0F5] text-[#7652D6] flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-[#29243A]">
                Choose AI Health Agents
              </h2>
              <p className="text-[11px] text-[#777187]">
                Click any agent below to turn it on or off for your questions
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <Badge 
              variant="outline" 
              className="text-xs bg-[#FFF0F5] text-[#7652D6] border-pink-200/80 rounded-full px-3 py-1 font-semibold"
            >
              {selectedAgents.length} of {CORE_MEDICAL_AGENTS.length} In Use
            </Badge>

            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
              className="h-7 px-2.5 text-[11px] font-semibold rounded-full border-pink-200 hover:bg-[#FFF0F5] text-[#7652D6]"
            >
              <CheckCheck className="w-3 h-3 mr-1" />
              Use All
            </Button>

            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleResetDefault}
              className="h-7 px-2 text-[11px] font-semibold rounded-full text-[#777187] hover:text-[#29243A] hover:bg-gray-100"
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              Reset
            </Button>
          </div>
        </div>

        {/* Dynamic Agent Cards Grid with Active/Excluded Toggling */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {CORE_MEDICAL_AGENTS.map((agent) => (
            <MedicalAgentCard
              key={agent.id}
              {...agent}
              selectable={true}
              selected={selectedAgents.includes(agent.id)}
              onToggle={toggleAgent}
            />
          ))}
        </div>
      </div>

    </div>
  );
}
