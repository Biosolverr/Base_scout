import os
import json
import logging
from groq import Groq
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SYSTEM_PROMPT = """You are a crypto ecosystem analyst specializing in Base blockchain.
Analyze projects and return ONLY a JSON array. No markdown, no explanation.
Each item must have exactly these fields:
- narrative: one of ["DeFi","AI agents","social","memecoins","creator tools","infrastructure","gaming","NFT","other"]
- why_interesting: one sentence, why this could matter on Base
- score: integer 1-5 (5 = most promising)
- tags: array of 2-4 short strings
- summary: 1-2 sentences about the project
"""
BATCH_SIZE = 10
def analyze_batch(items: list[dict]) -> list[dict]:
    enriched = []
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i + BATCH_SIZE]
        cards = [
            f"{j+1}. Name: {it.get('name','')} | URL: {it.get('url','')} | Desc: {it.get('description','')[:200]}"
            for j, it in enumerate(batch)
        ]
        prompt = "Analyze these Base ecosystem projects:\n\n" + "\n".join(cards)
        prompt += f"\n\nReturn a JSON array with exactly {len(batch)} objects in order."
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2000,
            )
            raw = resp.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(raw)
            for j, item in enumerate(batch):
                merged = {**item}
                if j < len(analysis):
                    merged.update(analysis[j])
                enriched.append(merged)
            logger.info(f"LLM batch {i//BATCH_SIZE+1}: {len(batch)} items done")
        except Exception as e:
            logger.warning(f"LLM batch error: {e}")
            for item in batch:
                enriched.append({**item, "narrative": "other", "score": 1, "tags": [], "summary": "", "why_interesting": ""})
    return enriched
