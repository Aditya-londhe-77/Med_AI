from enum import Enum

class SourceTier(str, Enum):
    TIER_1 = "Tier 1"  # Official, Gov, SEC, High Trust
    TIER_2 = "Tier 2"  # Major News, Reputable Orgs
    TIER_3 = "Tier 3"  # Blogs, Social Media, Opinion

# Confidence base scores
TIER_WEIGHTS = {
    SourceTier.TIER_1: 0.9,
    SourceTier.TIER_2: 0.7,
    SourceTier.TIER_3: 0.4
}

# LLM Models
FAST_MODEL = "gemini-1.5-flash-preview-0514"
REASONING_MODEL = "gemini-1.5-pro-preview-0514"

# RAG Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Orchestrator
MAX_DEBATE_ROUNDS = 2
AGENT_TIMEOUT_SECONDS = 60
