import { useState, useEffect, useRef } from 'react';
import { api } from '@/services/api';

// ── Event types ──────────────────────────────────────────────────────────────

export type AgentEventType =
  | 'system'
  | 'agent'
  | 'finding'
  | 'evidence'
  | 'challenge'
  | 'graph'
  // Rich medical sub-types from AISIA backend
  | 'agent_started'
  | 'agent_finding'
  | 'evidence_validated'
  | 'evidence_challenged'
  | 'synthesis_complete'
  | 'safety_check'
  | 'error';

export interface AgentEvent {
  id: number;
  type: AgentEventType;
  /** Visual bucket for colour-coding */
  displayType: 'system' | 'agent' | 'finding' | 'evidence' | 'challenge' | 'graph';
  text: string;
  time: string;
  // Optional rich fields
  agentId?: string;
  agentName?: string;
  model?: string;
  statement?: string;
  confidence?: number;
  domain?: string;
  sources?: string[];
  challengeText?: string;
  targetAgent?: string;
  totalFindings?: number;
  contradictions?: number;
  evidenceGaps?: number;
}

// Map backend event sub-type → display bucket
const DISPLAY_TYPE_MAP: Record<string, AgentEvent['displayType']> = {
  agent_started:        'agent',
  agent_finding:        'finding',
  evidence_validated:   'evidence',
  evidence_challenged:  'challenge',
  synthesis_complete:   'system',
  safety_check:         'system',
  agent:                'agent',
  finding:              'finding',
  claim:                'finding',
  evidence:             'evidence',
  challenge:            'challenge',
  graph:                'graph',
  system:               'system',
  error:                'challenge',
};

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useAgentStream(queryId: string | undefined) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [progress, setProgress] = useState(5);
  const [isComplete, setIsComplete] = useState(false);
  const [hasError, setHasError] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const pollingRef = useRef<any>(null);
  const wsConnectedRef = useRef(false);

  const addEvent = (rawType: string, text: string, extras?: Partial<AgentEvent>) => {
    const displayType = DISPLAY_TYPE_MAP[rawType] || 'system';
    setEvents(prev => {
      // Deduplicate consecutive identical messages
      if (prev.length > 0 && prev[prev.length - 1].text === text) return prev;
      return [
        ...prev,
        {
          id: Date.now() + Math.random(),
          type: rawType as AgentEventType,
          displayType,
          text,
          time: new Date().toLocaleTimeString([], {
            hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'
          }),
          ...extras,
        },
      ];
    });
  };

  useEffect(() => {
    if (!queryId) return;

    addEvent('system', 'Connecting to AISIA Medical AI Orchestration Swarm...');

    // ── 1. WebSocket ────────────────────────────────────────────────────────
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    try {
      const ws = new WebSocket(`${WS_URL}/${queryId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        wsConnectedRef.current = true;
        addEvent('system', '🔗 Connected to AISIA Live Clinical Telemetry Channel.');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const rawType = data.event || data.type || 'system';
          const text = data.message || '';

          if (text) {
            // Safely parse numeric confidence (protecting against objects such as confidence_metrics)
            let confVal: number | undefined = undefined;
            if (typeof data.confidence === 'number' && !isNaN(data.confidence)) {
              confVal = data.confidence > 1 ? Math.round(data.confidence) : Math.round(data.confidence * 100);
            } else if (typeof data.confidence === 'object' && data.confidence !== null) {
              const score = data.confidence.overall_score ?? data.confidence.global_score;
              if (typeof score === 'number' && !isNaN(score)) {
                confVal = score > 1 ? Math.round(score) : Math.round(score * 100);
              }
            }

            // Safely normalize sources to string array
            let sourcesList: string[] | undefined = undefined;
            if (Array.isArray(data.sources)) {
              sourcesList = data.sources.map((s: any) => typeof s === 'string' ? s : s?.title || 'Clinical Source');
            } else if (typeof data.sources === 'string' && data.sources) {
              sourcesList = [data.sources];
            }

            addEvent(rawType, text, {
              agentId:        data.agent_id,
              agentName:      data.agent_name,
              model:          data.model,
              statement:      data.statement,
              confidence:     confVal,
              domain:         data.domain,
              sources:        sourcesList,
              challengeText:  data.challenge_text,
              targetAgent:    data.target_agent,
              totalFindings:  data.total_findings,
              contradictions: data.contradictions,
              evidenceGaps:   data.evidence_gaps,
            });
          }

          if (data.progress) {
            setProgress(prev => Math.max(prev, data.progress));
          }

          if (data.status === 'completed' || data.progress >= 100 || data.event === 'completed') {
            setIsComplete(true);
            setProgress(100);
            if (pollingRef.current) clearInterval(pollingRef.current);
          } else if (data.status === 'failed' || data.event === 'error') {
            setHasError(true);
            if (pollingRef.current) clearInterval(pollingRef.current);
          }
        } catch {
          addEvent('system', event.data);
        }
      };

      ws.onerror = () => {
        if (!wsConnectedRef.current) {
          addEvent('system', '📡 Live WebSocket streaming offline — synchronizing via high-speed polling channel.');
        }
      };

      ws.onclose = () => {
        wsConnectedRef.current = false;
      };
    } catch {
      addEvent('system', '📡 Streaming via high-speed polling channel.');
    }

    // ── 2. REST polling fallback ────────────────────────────────────────────
    pollingRef.current = setInterval(async () => {
      try {
        const res = await api.fetchQueryResult(queryId);
        if (res && res.status === 'completed') {
          clearInterval(pollingRef.current);
          setProgress(100);
          addEvent('system', '✅ Evidence-grounded medical report compiled. Report ready.');
          setIsComplete(true);
        } else if (res && res.status === 'failed') {
          clearInterval(pollingRef.current);
          setHasError(true);
        }
      } catch {
        // Still processing or 404 not yet available — keep polling
      }
    }, 1500);

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [queryId]);

  return { events, progress, isComplete, hasError };
}

export const useMedicalStream = useAgentStream;
