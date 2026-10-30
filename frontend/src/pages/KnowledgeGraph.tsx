import { useEffect, useState, useMemo } from "react";
import { Network, Search, Info } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { LoadingState } from "@/components/ui/LoadingState";
import { api, type GraphNode, type GraphData } from "@/services/api";

const MEDICAL_NODE_COLORS: Record<string, { fill: string; stroke: string; text: string; badge: string }> = {
  Condition:    { fill: "#F3EEFF", stroke: "#7652D6", text: "#4B2B91", badge: "bg-[#F3EEFF] text-[#4B2B91] border-[#7652D6]/30" },
  Drug:         { fill: "#FFF1F7", stroke: "#E879B9", text: "#9D174D", badge: "bg-[#FFF1F7] text-[#E879B9] border-[#E879B9]/30" },
  Anatomy:      { fill: "#EEF2FF", stroke: "#6366F1", text: "#3730A3", badge: "bg-indigo-50 text-indigo-700 border-indigo-200" },
  Biomarker:    { fill: "#ECFDF5", stroke: "#10B981", text: "#065F46", badge: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  Organization: { fill: "#EFF6FF", stroke: "#3B82F6", text: "#1E40AF", badge: "bg-blue-50 text-blue-700 border-blue-200" },
  Default:      { fill: "#F9FAFB", stroke: "#9CA3AF", text: "#374151", badge: "bg-gray-50 text-gray-700 border-gray-200" },
};

export function KnowledgeGraph() {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("ALL");
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    setLoading(true);
    api.fetchGraphSubgraph()
      .then((data) => {
        setGraphData(data);
        if (data.nodes.length > 0) {
          setSelectedNode(data.nodes[0]);
        }
      })
      .catch((err) => {
        console.warn("Could not load medical knowledge graph", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const nodes = useMemo(() => graphData?.nodes || [], [graphData]);
  const links = useMemo(() => graphData?.links || [], [graphData]);

  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const matchesSearch = !searchQuery || n.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesType = selectedType === "ALL" || n.type === selectedType;
      return matchesSearch && matchesType;
    });
  }, [nodes, searchQuery, selectedType]);

  // Derive coordinates for elliptical interactive canvas
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const total = nodes.length;
    const centerX = 380;
    const centerY = 240;
    const radiusX = 270;
    const radiusY = 160;

    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / Math.max(total, 1);
      const rX = radiusX + (i % 2 === 0 ? 25 : -25);
      const rY = radiusY + (i % 2 === 0 ? -15 : 20);
      positions[node.id] = {
        x: Math.round(centerX + rX * Math.cos(angle)),
        y: Math.round(centerY + rY * Math.sin(angle)),
      };
    });
    return positions;
  }, [nodes]);

  // Relationships linked to currently selected node
  const linkedRelationships = useMemo(() => {
    if (!selectedNode) return [];
    return links.filter(
      (l) => l.source === selectedNode.id || l.target === selectedNode.id
    );
  }, [links, selectedNode]);

  if (loading) {
    return (
      <LoadingState
        message="Loading Medical Knowledge Explorer..."
        subtext="Querying Neo4j clinical ontology & relation graph"
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="border-b border-[#E9E2F2] pb-5 space-y-1.5">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#7652D6]/20 bg-[#F3EEFF] px-3.5 py-1 text-xs font-bold text-[#4B2B91]">
          <Network className="w-3.5 h-3.5 text-[#7652D6]" />
          <span>Health Knowledge Map</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#29243A] tracking-tight">
          Medical Knowledge Explorer
        </h1>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Category Filter Tabs */}
        <div className="flex flex-wrap gap-1.5">
          {[
            { key: "ALL", label: "All Topics" },
            { key: "Condition", label: "Diseases" },
            { key: "Drug", label: "Medicines" },
            { key: "Anatomy", label: "Body Parts" },
            { key: "Biomarker", label: "Health Markers" },
            { key: "Organization", label: "Health Bodies" },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setSelectedType(key)}
              className={`rounded-xl px-3 py-1.5 text-xs font-bold transition-all border ${
                selectedType === key
                  ? "bg-[#7652D6] text-white border-[#7652D6] shadow-sm shadow-[#7652D6]/20"
                  : "bg-white text-[#4B2B91] border-[#E9E2F2] hover:bg-[#F3EEFF]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#7652D6]" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search health topics..."
            className="h-9 rounded-xl border-[#E9E2F2] bg-white pl-9 text-xs text-[#29243A] focus:border-[#7652D6]"
          />
        </div>
      </div>

      {/* Interactive Visual Graph Canvas & Node Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* SVG Graph Canvas */}
        <Card className="lg:col-span-8 rounded-3xl border border-[#E9E2F2] bg-white shadow-sm overflow-hidden flex flex-col">
          <CardHeader className="py-3 px-5 border-b border-[#E9E2F2] bg-[#F3EEFF]/40 flex flex-row items-center justify-between">
            <span className="text-xs font-bold text-[#4B2B91]">
              Connection Map ({filteredNodes.length} topics shown)
            </span>
            <span className="text-[10px] text-[#777187] font-mono">
              Tap a topic to explore its connections
            </span>
          </CardHeader>

          <CardContent className="p-4 flex-1 flex items-center justify-center bg-[radial-gradient(#E9E2F2_1px,transparent_1px)] [background-size:16px_16px]">
            <svg
              viewBox="0 0 760 480"
              className="w-full h-[460px] select-none"
            >
              {/* Links */}
              {links.map((link, idx) => {
                const sPos = nodePositions[link.source];
                const tPos = nodePositions[link.target];
                if (!sPos || !tPos) return null;

                const isLinkedToSelected =
                  selectedNode &&
                  (link.source === selectedNode.id || link.target === selectedNode.id);

                return (
                  <g key={idx}>
                    <line
                      x1={sPos.x}
                      y1={sPos.y}
                      x2={tPos.x}
                      y2={tPos.y}
                      stroke={isLinkedToSelected ? "#7652D6" : "#E9E2F2"}
                      strokeWidth={isLinkedToSelected ? 2 : 1}
                      strokeDasharray={isLinkedToSelected ? "none" : "3,3"}
                      opacity={isLinkedToSelected ? 0.9 : 0.6}
                    />
                    {isLinkedToSelected && (
                      <text
                        x={(sPos.x + tPos.x) / 2}
                        y={(sPos.y + tPos.y) / 2 - 4}
                        fill="#7652D6"
                        fontSize={9}
                        fontWeight="bold"
                        textAnchor="middle"
                        className="font-mono bg-white"
                      >
                        {link.label}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Nodes */}
              {filteredNodes.map((node) => {
                const pos = nodePositions[node.id];
                if (!pos) return null;

                const isSelected = selectedNode?.id === node.id;
                const colors = MEDICAL_NODE_COLORS[node.type] || MEDICAL_NODE_COLORS.Default;

                return (
                  <g
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className="cursor-pointer transition-transform hover:scale-105"
                  >
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r={isSelected ? 22 : 16}
                      fill={colors.fill}
                      stroke={colors.stroke}
                      strokeWidth={isSelected ? 3 : 1.5}
                      className={isSelected ? "filter drop-shadow-md" : ""}
                    />
                    <text
                      x={pos.x}
                      y={pos.y + 28}
                      fill="#29243A"
                      fontSize={10}
                      fontWeight="bold"
                      textAnchor="middle"
                      className="pointer-events-none"
                    >
                      {node.name.length > 18 ? node.name.slice(0, 16) + "..." : node.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </CardContent>
        </Card>

        {/* Selected Topic Details */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="rounded-3xl border border-[#E9E2F2] bg-white shadow-sm overflow-hidden">
            <CardHeader className="py-4 px-5 border-b border-[#E9E2F2] bg-[#F3EEFF]/40">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-[#4B2B91] flex items-center gap-2">
                <Info className="w-3.5 h-3.5 text-[#7652D6]" />
                Topic Details
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              {selectedNode ? (
                <>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <Badge
                        variant="outline"
                        className={
                          MEDICAL_NODE_COLORS[selectedNode.type]?.badge ||
                          MEDICAL_NODE_COLORS.Default.badge
                        }
                      >
                        {selectedNode.type}
                      </Badge>
                      <span className="font-mono text-[10px] text-[#777187]">
                        ID: {selectedNode.id}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-[#29243A] tracking-tight">
                      {selectedNode.name}
                    </h3>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-[#E9E2F2]">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#777187]">
                      Connected To ({linkedRelationships.length})
                    </span>
                    <div className="space-y-2 max-h-56 overflow-y-auto">
                      {linkedRelationships.length > 0 ? (
                        linkedRelationships.map((rel, i) => (
                          <div
                            key={i}
                            className="p-2.5 rounded-xl bg-[#F3EEFF]/50 border border-[#E9E2F2] text-xs space-y-1"
                          >
                            <span className="text-[10px] font-bold text-[#7652D6] font-mono">
                              {rel.label}
                            </span>
                            <div className="text-[#29243A] font-medium text-[11px]">
                              {rel.source === selectedNode.id ? `→ ${rel.target}` : `← ${rel.source}`}
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-[#777187]">No connections found for this topic.</p>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-xs text-[#777187]">Tap any topic above to see its details and connections.</p>
              )}
            </CardContent>
          </Card>
        </div>

      </div>

    </div>
  );
}
