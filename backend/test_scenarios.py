import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.orchestrator.workflow import create_workflow
from app.shared.schemas import AgentRequest

SCENARIOS = [
    "ASML ArFi DUV lithography export licensing on Chinese foundries",
    "EU AI Act Regulation 2024/1689 Annex III compliance exposure",
    "Gallium and Germanium export restrictions on AESA radar supply chains",
    "Taiwan Strait commercial maritime container routing and war-risk premiums"
]

async def run_scenario(app, query: str):
    print(f"\n=======================================================")
    print(f"RUNNING SCENARIO: {query}")
    print(f"=======================================================")
    
    request = AgentRequest(query=query, session_id="test_sc")
    state = {
        "request": request,
        "all_claims": [],
        "agent_responses": {},
        "challenges": [],
        "round_count": 0,
        "final_briefing": {},
        "confidence_metrics": {}
    }
    
    result = await app.ainvoke(state)
    briefing = result.get("final_briefing", {})
    scenarios = briefing.get("scenarios", [])
    
    print("Briefing Title:", briefing.get("title"))
    print("Scenarios Generated:", len(scenarios))
    for s in scenarios:
        print(f"  - [{s['name']}] (Prob: {s['probability']}%, Impact: {s['impact']})")
    print("Global Confidence:", result.get("confidence_metrics", {}).get("global_score"))
    print("Total Claims Extracted:", len(briefing.get("claims", [])))

async def main():
    app = create_workflow()
    for sc in SCENARIOS:
        await run_scenario(app, sc)

if __name__ == "__main__":
    asyncio.run(main())
