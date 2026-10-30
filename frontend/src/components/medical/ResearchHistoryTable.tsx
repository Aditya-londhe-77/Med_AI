import { Link } from "react-router-dom";
import { ArrowUpRight, FileText, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { HistoryRecord } from "@/services/api";

interface ResearchHistoryTableProps {
  records: HistoryRecord[];
}

export function ResearchHistoryTable({ records }: ResearchHistoryTableProps) {
  if (!records || records.length === 0) {
    return (
      <div className="py-12 text-center text-xs text-[#777187]">
        No previous medical research queries recorded.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="bg-[#F3EEFF]/60 text-[#4B2B91] border-b border-[#E9E2F2]">
          <tr>
            <th className="py-3 px-4 font-bold uppercase tracking-wider text-[10px]">Medical Inquiry</th>
            <th className="py-3 px-4 font-bold uppercase tracking-wider text-[10px]">Domain</th>
            <th className="py-3 px-4 font-bold uppercase tracking-wider text-[10px]">Status</th>
            <th className="py-3 px-4 font-bold uppercase tracking-wider text-[10px]">Recorded</th>
            <th className="py-3 px-4 font-bold uppercase tracking-wider text-[10px] text-right">Report</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#E9E2F2]">
          {records.map((rec) => (
            <tr key={rec.id} className="hover:bg-[#F3EEFF]/30 transition-colors">
              <td className="py-3.5 px-4 font-semibold text-[#29243A] max-w-xs md:max-w-md truncate">
                <div className="flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5 text-[#7652D6] shrink-0" />
                  <span className="truncate">{rec.query_text}</span>
                </div>
              </td>
              <td className="py-3.5 px-4">
                <Badge variant="outline" className="text-[10px] bg-white border-[#E9E2F2] text-[#4B2B91]">
                  {rec.domain || "General Medicine"}
                </Badge>
              </td>
              <td className="py-3.5 px-4">
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3" />
                  Synthesized
                </span>
              </td>
              <td className="py-3.5 px-4 text-[#777187] font-mono text-[11px]">
                {rec.created_at ? new Date(rec.created_at).toLocaleDateString() : "Recent"}
              </td>
              <td className="py-3.5 px-4 text-right">
                <Link
                  to={`/results/${rec.id}`}
                  className="inline-flex items-center gap-1 font-bold text-[#7652D6] hover:text-[#4B2B91] hover:underline"
                >
                  <span>View Dossier</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
