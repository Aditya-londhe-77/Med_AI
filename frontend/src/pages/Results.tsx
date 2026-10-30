import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Printer,
  ArrowLeft,
  Share2,
  Check,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  BookOpen,
  Lightbulb,
  ArrowRight,
  Info,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { api, type MedicalQueryResult } from "@/services/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface StructuredSource {
  title: string;
  url?: string;
  org?: string;
  date?: string;
}

interface EvidenceDetails {
  total_findings?: number;
  high_confidence_findings?: number;
  contradictions?: string[];
  evidence_gaps?: string[];
  findings?: Array<{ statement: string; agent: string; confidence: number; domain: string; validated: boolean }>;
}

interface StructuredAnswer {
  direct_answer?: string;
  what_this_means?: string;
  next_steps?: string[];
  when_to_seek_help?: string;
  sources?: StructuredSource[];
  safety_note?: string;
  evidence_details?: EvidenceDetails;
  emergency_detected?: boolean;
  emergency_warning?: string;
}

// ── Collapsible panel ─────────────────────────────────────────────────────────

function Panel({ title, icon, children, defaultOpen = false }: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-2xl border border-pink-200/80 bg-white/95 shadow-sm overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-3 px-5 py-4 text-left hover:bg-[#FFF5F9] transition-colors"
      >
        <span className="flex items-center gap-2 text-sm font-bold text-[#4B2B91]">
          {icon}
          {title}
        </span>
        {open ? <ChevronUp className="w-4 h-4 text-[#7652D6]" /> : <ChevronDown className="w-4 h-4 text-[#7652D6]" />}
      </button>
      {open && <div className="px-5 pb-5 pt-0 text-sm text-[#29243A] leading-relaxed">{children}</div>}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function Results() {
  const { id } = useParams<{ id: string }>();

  const [data, setData] = useState<MedicalQueryResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!id) return;
    let isMounted = true;
    const fetchReport = async () => {
      try {
        const res = await api.fetchQueryResult(id);
        if (isMounted) { setData(res); setLoading(false); }
      } catch (err: any) {
        if (isMounted) { setError(err.message || "Failed to load health summary"); setLoading(false); }
      }
    };
    fetchReport();
    return () => { isMounted = false; };
  }, [id]);

  const handleCopy = () => {
    if (!data) return;
    const ans = getStructured(data);
    const text = [
      ans.direct_answer,
      ans.what_this_means,
      ans.next_steps?.map((s) => `• ${s}`).join("\n"),
    ].filter(Boolean).join("\n\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return <LoadingState message="Putting together your health summary..." subtext="Gathering evidence-grounded information" />;
  }
  if (error || !data) {
    return <ErrorState title="Could Not Load Health Summary" message={error || "Could not retrieve the requested health summary."} onRetry={() => window.location.reload()} />;
  }

  const ans = getStructured(data);
  const isEmergency = ans.emergency_detected || !!data.emergency_warning;
  const emergencyMsg = ans.emergency_warning || data.emergency_warning;

  return (
    <div className="mx-auto max-w-3xl space-y-6 pb-16 animate-in fade-in duration-500">

      {/* Top navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-pink-200/80 pb-4">
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-bold text-[#7652D6] hover:text-[#4B2B91] hover:underline">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <div className="flex items-center gap-2">
          <Button onClick={handleCopy} variant="outline" className="h-9 px-4 text-xs font-semibold rounded-full border-pink-200 text-[#4B2B91] hover:bg-[#FFF0F5] flex items-center gap-1.5">
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Share2 className="w-3.5 h-3.5" />}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button onClick={() => window.print()} variant="outline" className="h-9 px-4 text-xs font-semibold rounded-full border-pink-200 text-[#4B2B91] hover:bg-[#FFF0F5] flex items-center gap-1.5">
            <Printer className="w-3.5 h-3.5" />
            Print
          </Button>
        </div>
      </div>

      {/* Emergency banner */}
      {isEmergency && (
        <div className="rounded-2xl border border-red-300 bg-red-50 p-5 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-bold text-red-700 mb-1">Emergency — Seek Immediate Help</p>
            <p className="text-xs text-red-600 leading-relaxed">{emergencyMsg}</p>
          </div>
        </div>
      )}

      {/* Direct answer hero */}
      <div className="rounded-3xl border border-pink-200/80 bg-gradient-to-br from-white via-white to-[#FFF5F9] p-6 sm:p-8 shadow-lg shadow-pink-500/5 space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <Badge className="bg-[#7652D6] text-white hover:bg-[#4B2B91] text-[10px] font-bold rounded-full px-3 py-1">
            HEALTH ANSWER
          </Badge>
          {data.domain && (
            <Badge variant="outline" className="text-[10px] text-[#4B2B91] border-pink-200 bg-[#FFF0F5] rounded-full px-3 py-1">
              {data.domain}
            </Badge>
          )}
        </div>

        <p className="text-base sm:text-lg font-bold text-[#29243A] leading-relaxed">
          {ans.direct_answer || data.query_text}
        </p>
      </div>

      {/* What this means */}
      {ans.what_this_means && (
        <Panel title="What this means" icon={<Lightbulb className="w-4 h-4 text-amber-500" />} defaultOpen={true}>
          <p className="whitespace-pre-line">{ans.what_this_means}</p>
        </Panel>
      )}

      {/* Next steps */}
      {ans.next_steps && ans.next_steps.length > 0 && (
        <Panel title="What you can do next" icon={<ArrowRight className="w-4 h-4 text-emerald-600" />} defaultOpen={true}>
          <ul className="space-y-2.5 mt-1">
            {ans.next_steps.map((step, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="w-5 h-5 shrink-0 rounded-full bg-[#FFF0F5] border border-pink-200 flex items-center justify-center text-[10px] font-bold text-[#7652D6] mt-0.5">
                  {i + 1}
                </span>
                <span className="text-sm leading-relaxed">{step}</span>
              </li>
            ))}
          </ul>
        </Panel>
      )}

      {/* When to seek help */}
      {ans.when_to_seek_help && (
        <Panel title="When to seek help" icon={<ShieldCheck className="w-4 h-4 text-rose-600" />} defaultOpen={isEmergency}>
          <p className="whitespace-pre-line">{ans.when_to_seek_help}</p>
        </Panel>
      )}

      {/* Sources */}
      <Panel title={`Sources${ans.sources && ans.sources.length > 0 ? ` (${ans.sources.length})` : ""}`} icon={<BookOpen className="w-4 h-4 text-[#7652D6]" />} defaultOpen={false}>
        {ans.sources && ans.sources.length > 0 ? (
          <ul className="space-y-3 mt-1">
            {ans.sources.map((src, i) => (
              <li key={i} className="rounded-xl border border-pink-100 bg-[#FFF5F9]/60 p-3.5 space-y-0.5">
                {src.url ? (
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-semibold text-[#4B2B91] hover:underline flex items-center gap-1"
                  >
                    {src.title}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                ) : (
                  <p className="text-xs font-semibold text-[#4B2B91]">{src.title}</p>
                )}
                {(src.org || src.date) && (
                  <p className="text-[11px] text-[#777187]">
                    {[src.org, src.date].filter(Boolean).join(" · ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-[#777187] italic mt-1">
            No verified external sources were retrieved for this question. The answer is based on general medical knowledge.
            Please consult a healthcare professional for source-backed guidance.
          </p>
        )}
      </Panel>

      {/* Safety note */}
      {ans.safety_note && (
        <div className="flex items-start gap-2.5 rounded-2xl border border-pink-100 bg-[#FFF5F9]/80 px-4 py-3">
          <Info className="w-4 h-4 text-[#7652D6] mt-0.5 shrink-0" />
          <p className="text-xs text-[#777187] leading-relaxed">{ans.safety_note}</p>
        </div>
      )}

      {/* Evidence details (power-user panel) */}
      {ans.evidence_details && (
        <Panel title="How was this answer generated?" icon={<Info className="w-4 h-4 text-[#7652D6]" />} defaultOpen={false}>
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: "Findings", value: ans.evidence_details.total_findings ?? 0 },
                { label: "High confidence", value: ans.evidence_details.high_confidence_findings ?? 0 },
                { label: "Contradictions", value: ans.evidence_details.contradictions?.length ?? 0 },
                { label: "Evidence gaps", value: ans.evidence_details.evidence_gaps?.length ?? 0 },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-xl border border-pink-100 bg-white p-3 text-center">
                  <p className="text-xl font-extrabold text-[#7652D6]">{value}</p>
                  <p className="text-[10px] text-[#777187] mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {ans.evidence_details.contradictions && ans.evidence_details.contradictions.length > 0 && (
              <div>
                <p className="text-xs font-bold text-[#4B2B91] mb-1.5">Contradictions noted</p>
                <ul className="space-y-1">
                  {ans.evidence_details.contradictions.map((c, i) => (
                    <li key={i} className="text-xs text-[#777187] flex items-start gap-1.5">
                      <span className="text-amber-500 mt-0.5">⚠</span> {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {ans.evidence_details.evidence_gaps && ans.evidence_details.evidence_gaps.length > 0 && (
              <div>
                <p className="text-xs font-bold text-[#4B2B91] mb-1.5">Evidence gaps</p>
                <ul className="space-y-1">
                  {ans.evidence_details.evidence_gaps.map((g, i) => (
                    <li key={i} className="text-xs text-[#777187] flex items-start gap-1.5">
                      <span className="text-[#7652D6] mt-0.5">·</span> {g}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {ans.evidence_details.findings && ans.evidence_details.findings.length > 0 && (
              <div>
                <p className="text-xs font-bold text-[#4B2B91] mb-1.5">Agent findings</p>
                <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                  {ans.evidence_details.findings.map((f, i) => (
                    <div key={i} className="rounded-xl border border-pink-100 bg-white p-3 space-y-1">
                      <p className="text-xs text-[#29243A] leading-snug">{f.statement}</p>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] text-[#7652D6] bg-[#FFF0F5] rounded-full px-2 py-0.5 font-semibold">
                          {f.agent?.replace("_agent", "").replace("_", " ")}
                        </span>
                        <span className="text-[10px] text-emerald-700 bg-emerald-50 rounded-full px-2 py-0.5 font-semibold">
                          {f.confidence}% confidence
                        </span>
                        {f.validated && (
                          <span className="text-[10px] text-blue-700 bg-blue-50 rounded-full px-2 py-0.5 font-semibold">
                            Validated
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Panel>
      )}

    </div>
  );
}

// ── Helper: extract structured answer from the API response ───────────────────

function getStructured(data: any): StructuredAnswer {
  const report = data.report || data.briefing || {};

  // New schema
  if (report.direct_answer) {
    return report as StructuredAnswer;
  }

  // Legacy schema — map to new fields so the UI still works
  const findings: any[] = data.findings || data.claims || [];
  const topStatements = findings
    .sort((a: any, b: any) => (b.confidence_score || 0) - (a.confidence_score || 0))
    .slice(0, 3)
    .map((f: any) => f.statement || "");

  return {
    direct_answer: report.executive_summary || topStatements[0] || data.query_text,
    what_this_means: report.sections?.find((s: any) => s.section_type === "overview")?.content || "",
    next_steps: topStatements.slice(1),
    when_to_seek_help: report.sections?.find((s: any) => s.section_type === "safety")?.content || "",
    sources: [],
    safety_note: report.safety_disclaimer || "This information is for educational purposes only and does not replace professional medical advice.",
    evidence_details: {
      total_findings: findings.length,
      high_confidence_findings: findings.filter((f: any) => (f.confidence_score || 0) >= 0.8).length,
      contradictions: [],
      evidence_gaps: [],
      findings: findings.map((f: any) => ({
        statement: f.statement,
        agent: f.agent_id,
        confidence: Math.round((f.confidence_score || 0) * 100),
        domain: f.domain,
        validated: f.validated,
      })),
    },
    emergency_detected: data.emergency_detected || false,
    emergency_warning: data.emergency_warning || report.emergency_warning || "",
  };
}
