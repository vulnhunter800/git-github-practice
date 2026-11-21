"""Small, transparent heuristics for highlighting possible AI-related URLs."""

AI_ROUTE_KEYWORDS = (
    "openai", "anthropic", "llm", "chat", "completion", "completions",
    "embedding", "embeddings", "generative", "generation", "inference",
    "model", "prompt", "assistant", "agent", "rag", "vector", "ai",
)


def is_candidate_ai_url(url: str) -> bool:
    """Return True when a URL contains a likely AI-related route keyword."""
    lowered = url.lower()
    return any(keyword in lowered for keyword in AI_ROUTE_KEYWORDS)


def find_candidate_ai_urls(urls: list[str]) -> list[str]:
    """Return unique candidate URLs while preserving their original order."""
    seen = set()
    matches = []
    for url in urls:
        if url not in seen and is_candidate_ai_url(url):
            seen.add(url)
            matches.append(url)
    return matches
