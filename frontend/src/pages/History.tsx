import { useEffect, useState, useMemo } from "react";
import { History as HistoryIcon, Search, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LoadingState } from "@/components/ui/LoadingState";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { ResearchHistoryTable } from "@/components/medical/ResearchHistoryTable";
import { api, type HistoryRecord } from "@/services/api";

export function History() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.fetchHistory(50, 0);
      setRecords(data);
    } catch (err: any) {
      setError(err.message || "Failed to load clinical research history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) return records;
    return records.filter(
      (r) =>
        r.query_text.toLowerCase().includes(search.toLowerCase()) ||
        (r.domain && r.domain.toLowerCase().includes(search.toLowerCase()))
    );
  }, [records, search]);

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-pink-200/80 pb-5">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 rounded-full border border-pink-200 bg-[#FFF0F5] px-3.5 py-1 text-xs font-bold text-[#4B2B91]">
            <HistoryIcon className="w-3.5 h-3.5 text-pink-500" />
            <span>Past Questions & Answers</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#29243A] tracking-tight">
            Search History
          </h1>
        </div>

        <Button
          onClick={loadHistory}
          variant="outline"
          className="h-9 px-4 rounded-full border-pink-200 text-[#4B2B91] hover:bg-[#FFF0F5] text-xs font-bold flex items-center gap-1.5 self-start sm:self-auto transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5 text-pink-500" />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="absolute left-3.5 top-3 h-4 w-4 text-[#7652D6]" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by question or health topic..."
          className="h-10 rounded-full border-pink-200 bg-white pl-10 text-xs text-[#29243A] focus:border-pink-400"
        />
      </div>

      {/* Content */}
      {loading ? (
        <LoadingState
          message="Loading Your Past Questions..."
          subtext="Fetching your saved health question records"
        />
      ) : error ? (
        <ErrorState
          title="Could Not Load History"
          message={error}
          onRetry={loadHistory}
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No previous questions found"
          description={
            search ? "No records match your search filter." : "Ask your first health question in the Medical Workshop."
          }
          actionLabel="Open Medical Workshop"
          onAction={() => window.location.assign("/workspace")}
        />
      ) : (
        <div className="rounded-3xl border border-pink-200/80 bg-white/95 backdrop-blur-sm shadow-md overflow-hidden">
          <ResearchHistoryTable records={filtered} />
        </div>
      )}

    </div>
  );
}
