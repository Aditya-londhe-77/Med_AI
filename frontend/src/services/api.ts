const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface MedicalSourceCitation {
  id?: string;
  title: string;
  url?: string;
  grade?: string; // "Grade A", "Grade B", "Grade C"
  source_type?: string;
  snippet?: string;
  is_ai_generated?: boolean;
}

export interface MedicalFinding {
  id: string;
  statement: string;
  confidence_score: number;
  domain?: string;
  agent_id: string;
  finding_type?: string;
  sources: MedicalSourceCitation[];
  validated?: boolean;
  validation_notes?: string;
  disclaimer?: string;
}

// Backward compatibility alias
export type Claim = MedicalFinding;
export type SourceCitation = MedicalSourceCitation;

export interface MedicalReportSection {
  title: string;
  content: string;
  section_type: "overview" | "clinical_info" | "medication" | "evidence" | "safety" | string;
  citations?: string[];
}

export interface MedicalReport {
  title?: string;
  executive_summary?: string;
  key_findings?: string[];
  sections?: MedicalReportSection[];
  evidence_summary?: {
    total_findings?: number;
    high_confidence_findings?: number;
    contradictions_count?: number;
    evidence_gaps_count?: number;
  };
  recommendations?: string[];
  findings?: MedicalFinding[];
  safety_disclaimer?: string;
  emergency_warning?: string;
  safety_validated?: boolean;
  analysis_mode?: string;
}

// Backward compatibility alias
export type BriefingData = MedicalReport;

export interface ConfidenceMetrics {
  overall_score?: number;
  global_score?: number;
  total_findings?: number;
  grade_a_sources?: number;
  contradictions?: number;
  evidence_gaps?: number;
  evidence_richness?: number;
  consensus_score?: number;
}

export interface AgentTraceEvent {
  type?: string;
  time?: string;
  agent_id?: string;
  agent_name?: string;
  model?: string;
  message?: string;
  finding_id?: string;
  statement?: string;
  confidence?: number;
  domain?: string;
  sources?: string[];
  challenge_text?: string;
  total_findings?: number;
  contradictions?: number;
  evidence_gaps?: number;
}

export interface MedicalQueryResult {
  query_id: string;
  status: "processing" | "completed" | "failed";
  query_text: string;
  report?: MedicalReport;
  briefing?: MedicalReport; // backward compatibility
  confidence: ConfidenceMetrics;
  findings: MedicalFinding[];
  claims?: MedicalFinding[]; // backward compatibility
  agent_events?: AgentTraceEvent[];
  domain?: string;
  emergency_warning?: string;
  analysis_mode?: "gemini" | "heuristic_fallback" | string;
  llm_configured?: boolean;
  created_at?: string;
}

export type QueryResult = MedicalQueryResult;

export interface HistoryRecord {
  id: string;
  query_text: string;
  status: "processing" | "completed" | "failed";
  created_at: string;
  domain?: string;
}

export interface GraphNode {
  id: string;
  name: string;
  type: string; // "Condition", "Drug", "Anatomy", "Organization", "Biomarker"
  tier?: string;
}

export interface GraphLink {
  source: string;
  target: string;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  source?: string;
  note?: string;
}

export interface MedicalAgentInfo {
  id: string;
  name: string;
  role: string;
  model: string;
  tools: string[];
  status: string;
}

export interface SystemConfig {
  platform?: string;
  domain?: string;
  agents: Record<string, any>;
  parameters: {
    max_validation_rounds: number;
    evidence_grade_threshold: string;
    graph_traversal_hops: number;
    timeout_seconds: number;
  };
  integrations: Record<string, string>;
  domain_restriction?: string;
  llm_configured?: boolean;
}

export const api = {
  async submitQuery(
    query: string,
    agents?: string[],
    options?: { max_rounds?: number; source_tier?: number; include_medication?: boolean; include_clinical?: boolean; selected_agents?: string[] }
  ): Promise<{ message: string; query_id: string; emergency_warning?: string; platform?: string }> {
    const chosenAgents = agents || options?.selected_agents;
    const response = await fetch(`${API_BASE_URL}/medical/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_validation_rounds: options?.max_rounds ?? 1,
        include_medication_info: options?.include_medication ?? (chosenAgents ? chosenAgents.includes("medication_agent") : true),
        include_clinical_analysis: options?.include_clinical ?? (chosenAgents ? chosenAgents.includes("clinical_agent") : true),
        selected_agents: chosenAgents,
      })
    });

    if (!response.ok) {
      if (response.status === 422) {
        const errorData = await response.json();
        const detail = errorData.detail;
        const msg = typeof detail === 'object' && detail?.message ? detail.message : (detail || 'Query rejected.');
        throw new Error(`Domain Restriction: ${msg}`);
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  },

  async fetchHistory(limit = 20, offset = 0): Promise<HistoryRecord[]> {
    const response = await fetch(
      `${API_BASE_URL}/history?limit=${limit}&offset=${offset}`
    );
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    const data = await response.json();
    return data.history as HistoryRecord[];
  },

  async fetchQueryResult(queryId: string): Promise<MedicalQueryResult> {
    const response = await fetch(`${API_BASE_URL}/medical/query/${queryId}`);
    if (!response.ok) {
      // Fallback to general query path if needed
      const fallbackResp = await fetch(`${API_BASE_URL}/query/${queryId}`);
      if (!fallbackResp.ok) {
        throw new Error(`Failed to fetch query result: ${response.statusText}`);
      }
      return fallbackResp.json();
    }
    return response.json();
  },

  async fetchGraphSubgraph(query?: string): Promise<GraphData> {
    const url = query
      ? `${API_BASE_URL}/knowledge/graph?query=${encodeURIComponent(query)}`
      : `${API_BASE_URL}/knowledge/graph`;
    const response = await fetch(url);
    if (!response.ok) {
      // Fallback
      const fb = await fetch(`${API_BASE_URL}/graph/subgraph`);
      if (!fb.ok) throw new Error(`Failed to fetch graph data: ${response.statusText}`);
      return fb.json();
    }
    return response.json();
  },

  async fetchMedicalAgents(): Promise<MedicalAgentInfo[]> {
    const response = await fetch(`${API_BASE_URL}/agents`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.agents || [];
  },

  async fetchSystemConfig(): Promise<SystemConfig> {
    const response = await fetch(`${API_BASE_URL}/config`);
    if (!response.ok) {
      throw new Error(`Failed to fetch system configuration: ${response.statusText}`);
    }
    return response.json();
  }
};
