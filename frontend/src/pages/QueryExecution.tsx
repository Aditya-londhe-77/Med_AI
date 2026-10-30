import { useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { 
  Sparkles, 
  ArrowRight, 
  Activity, 
  BookOpen
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAgentStream } from "@/hooks/useAgentStream";
import { AgentWorkflowTimeline, type TimelineStep } from "@/components/medical/AgentWorkflowTimeline";
import { MedicalSafetyAlert } from "@/components/medical/MedicalSafetyAlert";
import { cn } from "@/lib/utils";

const MEDICAL_AGENT_TAGS: Record<string, { name: string; bg: string; text: string; border: string }> = {
  intake_agent: {
    name: "Question Helper",
    bg: "bg-[#FFF0F5]",
    text: "text-[#7652D6]",
    border: "border-pink-200",
  },
  literature_agent: {
    name: "Research Helper",
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
  },
  clinical_agent: {
    name: "Condition Guide",
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    border: "border-emerald-200",
  },
  medication_agent: {
    name: "Medicine Guide",
    bg: "bg-purple-50",
    text: "text-purple-700",
    border: "border-purple-200",
  },
  evidence_agent: {
    name: "Fact Checker",
    bg: "bg-[#FFF0F5]",
    text: "text-[#E879B9]",
    border: "border-pink-200",
  },
  synthesis_agent: {
    name: "Report Writer",
    bg: "bg-[#FFF0F5]",
    text: "text-[#4B2B91]",
    border: "border-pink-200",
  },
  safety_guard_agent: {
    name: "Safety Helper",
    bg: "bg-amber-50",
    text: "text-amber-700",
    border: "border-amber-200",
  },
};

export function QueryExecution() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const stateData = location.state as {
    query?: string;
    selectedDomain?: string;
    emergencyWarning?: string;
    selectedAgents?: string[];
  } | null;

  const { events, progress, isComplete } = useAgentStream(id);
  const [queryText] = useState(stateData?.query || "Your Health Question");

  // Friendly 5-step progress timeline
  const pipelineSteps: TimelineStep[] = [
    {
      id: "intake",
      label: "1. Reading & Understanding Your Question",
      description: "Understands the symptoms, conditions, or medicines you are asking about.",
      status: progress >= 20 ? "completed" : progress > 5 ? "running" : "pending",
    },
    {
      id: "research",
      label: "2. Finding Trusted Medical Information",
      description: "Searches medical guidelines, research articles, and health resources.",
      status: progress >= 50 ? "completed" : progress >= 20 ? "running" : "pending",
    },
    {
      id: "validation",
      label: "3. Double-Checking Facts & Accuracy",
      description: "Checks that all medical facts are consistent, accurate, and trustworthy.",
      status: progress >= 75 ? "completed" : progress >= 50 ? "running" : "pending",
    },
    {
      id: "synthesis",
      label: "4. Writing an Easy-to-Read Summary",
      description: "Organizes the findings into simple, plain English that is easy to understand.",
      status: progress >= 90 ? "completed" : progress >= 75 ? "running" : "pending",
    },
    {
      id: "safety",
      label: "5. Final Safety & Disclaimer Check",
      description: "Applies important patient safety notices and emergency guidance.",
      status: progress >= 100 ? "completed" : progress >= 90 ? "running" : "pending",
    },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* Emergency Notice if passed in state */}
      {stateData?.emergencyWarning && (
        <MedicalSafetyAlert
          type="emergency"
          title="Important Emergency Notice"
          message={stateData.emergencyWarning}
        />
      )}

      {/* Header Banner - Soft Rounded Design */}
      <div className="rounded-3xl border border-pink-200/80 bg-white/95 backdrop-blur-sm p-6 sm:p-8 shadow-lg shadow-pink-500/5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge className="bg-[#7652D6] text-white hover:bg-[#4B2B91] border-none text-[10px] font-bold rounded-full px-3 py-0.5">
              ID: {id?.slice(0, 8)}
            </Badge>
            {stateData?.selectedDomain && (
              <Badge variant="outline" className="text-[10px] text-[#4B2B91] border-pink-200 bg-[#FFF0F5] rounded-full px-3 py-0.5">
                {stateData.selectedDomain}
              </Badge>
            )}
            {stateData?.selectedAgents && (
              <Badge variant="outline" className="text-[10px] text-[#7652D6] border-pink-200 bg-[#FFF0F5] font-semibold rounded-full px-3 py-0.5">
                {stateData.selectedAgents.length} Agents Assigned
              </Badge>
            )}
            <Badge
              variant="outline"
              className={cn(
                "text-[10px] font-bold rounded-full px-3 py-0.5",
                isComplete
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : "bg-[#FFF0F5] text-pink-600 border-pink-200 animate-pulse"
              )}
            >
              {isComplete ? "Answer Ready" : "Helpers Working..."}
            </Badge>
          </div>

          <h1 className="text-xl sm:text-2xl font-extrabold text-[#29243A] tracking-tight">
            {queryText}
          </h1>
        </div>

        {isComplete && (
          <Button
            onClick={() => navigate(`/results/${id}`)}
            className="h-11 px-6 rounded-full bg-gradient-to-r from-[#7652D6] via-[#E879B9] to-[#F472B6] text-white font-bold text-xs sm:text-sm shadow-md shadow-pink-500/20 flex items-center gap-2 shrink-0 animate-bounce duration-1000"
          >
            <span>View Health Report</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-[#777187]">
          <span className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-pink-600" />
            Answer Progress
          </span>
          <span className="font-mono text-[#4B2B91] font-bold">{progress}%</span>
        </div>
        <Progress value={progress} className="h-2.5 rounded-full bg-pink-100" />
      </div>

      {/* Main Grid: Steps on Left, Live Telemetry on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Timeline */}
        <div className="lg:col-span-5 space-y-6">
          <AgentWorkflowTimeline steps={pipelineSteps} currentProgress={progress} />
          
          <MedicalSafetyAlert
            type="disclaimer"
            title="Double-Checking Active"
            message="All answers are verified by our Accuracy Checker before being included in your final health report."
          />
        </div>

        {/* Right Column: Live Telemetry Stream */}
        <div className="lg:col-span-7">
          <Card className="rounded-3xl border border-pink-200/80 bg-white/95 backdrop-blur-sm shadow-md overflow-hidden flex flex-col h-[600px]">
            <CardHeader className="py-4 px-5 border-b border-pink-100 bg-[#FFF5F9] flex flex-row items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-pink-600" />
                <CardTitle className="text-sm font-bold text-[#29243A]">
                  Live Research & Findings
                </CardTitle>
              </div>
              <span className="text-[11px] font-mono text-[#777187]">
                {events.length} Updates Logged
              </span>
            </CardHeader>

            <CardContent className="p-0 flex-1 overflow-hidden">
              <ScrollArea className="h-full p-4">
                <div className="space-y-3">
                  {events.map((ev) => {
                    const agentTag = MEDICAL_AGENT_TAGS[ev.agentId || ""] || {
                      name: ev.agentName || "System",
                      bg: "bg-gray-100",
                      text: "text-gray-700",
                      border: "border-gray-200",
                    };

                    const isFinding = ev.type === "agent_finding";
                    const isChallenge = ev.type === "evidence_challenged";
                    const isSystem = ev.type === "system";

                    return (
                      <div
                        key={ev.id}
                        className={cn(
                          "rounded-2xl p-3.5 text-xs transition-all border animate-in fade-in space-y-1.5",
                          isFinding && "bg-white border-pink-200/80 shadow-2xs",
                          isChallenge && "bg-amber-50/50 border-amber-200 text-amber-900",
                          isSystem && "bg-[#FFF5F9] border-pink-100 text-[#4B2B91]",
                          !isFinding && !isChallenge && !isSystem && "bg-white border-pink-100"
                        )}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono text-[#777187]">{ev.time}</span>
                            <Badge
                              variant="outline"
                              className={cn(
                                "text-[9px] font-bold uppercase tracking-wider py-0 px-2 rounded-full",
                                agentTag.bg,
                                agentTag.text,
                                agentTag.border
                              )}
                            >
                              {agentTag.name}
                            </Badge>
                          </div>
                          {typeof ev.confidence === 'number' && !isNaN(ev.confidence) && (
                            <span className="font-mono text-[10px] text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                              {ev.confidence}% Reliability
                            </span>
                          )}
                        </div>

                        <p className="text-[#29243A] leading-relaxed font-medium">
                          {typeof ev.text === 'object' ? JSON.stringify(ev.text) : String(ev.text ?? '')}
                        </p>

                        {ev.statement && typeof ev.statement === 'string' && ev.statement !== ev.text && (
                          <div className="p-2.5 rounded-xl bg-[#FFF5F9] border border-pink-100 text-[11px] text-[#29243A] italic">
                            "{ev.statement}"
                          </div>
                        )}

                        {Array.isArray(ev.sources) && ev.sources.length > 0 && (
                          <div className="flex items-center gap-1.5 pt-1 text-[10px] text-[#777187]">
                            <BookOpen className="w-3 h-3 text-[#7652D6]" />
                            <span className="truncate">
                              Sources: {ev.sources.map((s: any) => typeof s === 'string' ? s : s?.title || 'Clinical Source').join(", ")}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            </CardContent>

            {/* Bottom Footer Call-to-action */}
            {isComplete && (
              <div className="p-4 border-t border-pink-100 bg-[#FFF5F9] flex items-center justify-between">
                <span className="text-xs font-bold text-[#4B2B91]">
                  ✓ Fact-checking and health report complete.
                </span>
                <Button
                  onClick={() => navigate(`/results/${id}`)}
                  className="h-9 px-5 rounded-full bg-gradient-to-r from-[#7652D6] to-[#E879B9] hover:opacity-90 text-white text-xs font-bold shadow-xs"
                >
                  View Summary
                </Button>
              </div>
            )}
          </Card>
        </div>

      </div>

    </div>
  );
}
