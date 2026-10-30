import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.orchestrator.workflow import create_workflow
from app.shared.schemas import AgentRequest

async def main():
    print("Initializing workflow...")
    app = create_workflow()
    
    print("Creating AgentRequest...")
    request = AgentRequest(
        query="What will happen if commercial shipping through the Taiwan Strait is blockaded?", 
        session_id="test_taiwan_456"
    )
    
    initial_state = {
        "request": request,
        "all_claims": [],
        "agent_responses": {},
        "challenges": [],
        "round_count": 0,
        "final_briefing": {},
        "confidence_metrics": {}
    }
    
    print("Invoking LangGraph workflow...")
    try:
        result = await app.ainvoke(initial_state)
        briefing = result.get("final_briefing", {})
        print("\n=== TEST RESULTS ===")
        print("Rounds Taken:", result.get("round_count"))
        print("Final Briefing Title:", briefing.get("title"))
        print("Executive Summary:", briefing.get("executive_summary"))
        print("\n--- PREDICTIVE SCENARIOS ---")
        for sc in briefing.get("scenarios", []):
            print(f"  [{sc['name']}] (Probability: {sc['probability']}%, Impact: {sc['impact']})")
            print(f"    {sc['description']}")
        print("\n--- TIMELINE HORIZONS ---")
        print("  30D:", briefing.get("timeline_horizons", {}).get("horizon_30d"))
        print("  90D:", briefing.get("timeline_horizons", {}).get("horizon_90d"))
        print("  180D:", briefing.get("timeline_horizons", {}).get("horizon_180d"))
        print("\nTotal Claims Extracted:", len(briefing.get("claims", [])))
        print("Confidence Metrics:", result.get("confidence_metrics"))
        print("Challenges generated:", len(result.get("challenges", [])))
    except Exception as e:
        print(f"Error during workflow execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
