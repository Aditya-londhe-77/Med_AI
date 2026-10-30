import statistics
from typing import List, Dict, Any
from app.shared.schemas import Claim

class ConfidenceEngine:
    """
    Implements the confidence scoring architecture defined in the Master Implementation Plan.
    Calculates per-claim confidence and aggregates global confidence metrics.
    """
    ALPHA = 0.1        # Weight per supporting/contradicting source
    BETA = 0.2         # Weight for challenge survival
    MIN_CONFIDENCE = 0.1
    MAX_CONFIDENCE = 1.0
    
    def score_claim(self, claim: Claim, challenge_survived: bool = False, support_count: int = 1, contradict_count: int = 0) -> float:
        base = claim.confidence_score
        evidence_delta = self.ALPHA * (support_count - contradict_count)
        
        # Only apply challenge delta if the claim was actually challenged
        challenge_delta = 0
        if claim.challenged:
            challenge_delta = self.BETA * (1 if challenge_survived else -1)
            
        final_score = max(self.MIN_CONFIDENCE, min(self.MAX_CONFIDENCE, base + evidence_delta + challenge_delta))
        claim.confidence_score = final_score
        return final_score
    
    def global_confidence(self, claims: List[Claim]) -> Dict[str, Any]:
        if not claims:
            return {
                "global_score": 0.0,
                "evidence_richness": 0.0,
                "consensus_score": 0.0,
                "challenge_survival_rate": 0.0
            }
            
        claim_scores = [c.confidence_score for c in claims]
        trust_scores = []
        for c in claims:
            for s in c.sources:
                # Approximate trust score based on tier
                ts = 0.9 if s.tier.value == "Tier 1" else (0.7 if s.tier.value == "Tier 2" else 0.4)
                trust_scores.append(ts)
                
        mean_claim_score = statistics.mean(claim_scores) if claim_scores else 0.0
        mean_trust_score = statistics.mean(trust_scores) if trust_scores else 0.0
        
        global_score = mean_claim_score * mean_trust_score
        evidence_richness = len(trust_scores) / max(len(claims), 1)
        consensus_score = 1.0 - statistics.stdev(claim_scores) if len(claim_scores) > 1 else 1.0
        survival_rate = sum(1 for c in claims if not c.challenged) / max(len(claims), 1)
        
        return {
            "global_score": round(global_score, 2),
            "evidence_richness": round(evidence_richness, 2),
            "consensus_score": round(consensus_score, 2),
            "challenge_survival_rate": round(survival_rate, 2)
        }
