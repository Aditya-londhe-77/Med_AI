import { AlertTriangle, ShieldAlert, PhoneCall, Info } from "lucide-react";

interface MedicalSafetyAlertProps {
  type?: "emergency" | "disclaimer" | "domain_warning";
  title?: string;
  message?: string;
}

export function MedicalSafetyAlert({
  type = "disclaimer",
  title,
  message,
}: MedicalSafetyAlertProps) {
  if (type === "emergency") {
    return (
      <div className="relative overflow-hidden rounded-2xl border-2 border-red-500 bg-red-50 p-4 md:p-5 shadow-lg shadow-red-500/10">
        <div className="flex items-start gap-3.5">
          <div className="rounded-xl bg-red-600 p-2 text-white shadow-sm shrink-0">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <div className="space-y-1.5 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-red-700 bg-red-200/70 px-2 py-0.5 rounded-md">
                Critical Safety Alert
              </span>
              <h4 className="text-sm md:text-base font-bold text-red-950">
                {title || "Urgent Emergency Notice"}
              </h4>
            </div>
            <p className="text-xs md:text-sm text-red-900 leading-relaxed font-medium">
              {message || (
                "The symptoms or query entered suggest a potentially life-threatening emergency. If you or someone you are with is experiencing severe chest pain, stroke symptoms, respiratory distress, or severe poisoning, immediately call your local emergency services (911 in US, 112 in Europe, 108 in India) or proceed to the nearest emergency department."
              )}
            </p>
            <div className="pt-2 flex flex-wrap items-center gap-3 text-xs font-bold text-red-700">
              <span className="inline-flex items-center gap-1.5 rounded-lg bg-red-100 px-3 py-1.5 border border-red-200">
                <PhoneCall className="w-3.5 h-3.5 text-red-600" />
                Emergency Hotline: 911 / 112 / 108
              </span>
              <span className="text-[11px] font-medium text-red-600">
                AISIA is an informational AI platform, NOT a substitute for emergency medicine.
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (type === "domain_warning") {
    return (
      <div className="rounded-2xl border border-amber-300 bg-amber-50 p-4 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-amber-500 p-2 text-white shrink-0">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-amber-950">
              {title || "Medical Domain Restriction"}
            </h4>
            <p className="text-xs text-amber-900 leading-relaxed">
              {message || (
                "AISIA exclusively accepts queries related to healthcare, biomedical research, pharmacology, and clinical education."
              )}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-pink-200/70 bg-white/80 backdrop-blur-sm p-4 shadow-xs">
      <div className="flex items-start gap-3">
        <div className="rounded-full bg-gradient-to-tr from-[#7652D6] to-[#E879B9] p-2 text-white shrink-0 mt-0.5 shadow-xs">
          <Info className="h-3.5 w-3.5" />
        </div>
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[#4B2B91]">
            {title || "Important Health Notice"}
          </h4>
          <p className="text-[11px] sm:text-xs text-[#777187] leading-relaxed">
            {message || (
              "AI_Based_Strategic_Intelligence_Assistant_Medical_AI provides general health education and research summaries only. It does not provide medical diagnoses or personalized treatment plans. Always consult a licensed doctor or healthcare specialist for personal medical questions."
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
