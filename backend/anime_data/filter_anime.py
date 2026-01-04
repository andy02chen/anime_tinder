import json
from pathlib import Path

INPUT_DIR = Path("./")
OUTPUT_FILE = Path("anime_vector_store.json")

filtered_anime = []

import re
import unicodedata

def normalize_synopsis(text: str) -> str:
    if not text:
        return ""

    # Normalize unicode (quotes, dashes, etc.)
    text = unicodedata.normalize("NFKC", text)

    # Remove MAL boilerplate
    text = re.sub(
        r"\[\s*(written by|source:).*?\]",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Replace newlines and tabs with spaces
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()

for file_path in INPUT_DIR.glob("*.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        page = json.load(f)

    for item in page.get("data", []):
        node = item.get("node", {})

        anime_id = node.get("id")
        title = node.get("title", "").strip()
        raw_synopsis = node.get("synopsis", "")
        synopsis = normalize_synopsis(raw_synopsis)

        genres = [
            g["name"]
            for g in node.get("genres", [])
            if "name" in g
        ]

        if not synopsis:
            continue  # skip entries without usable text

        combined_text = (
            f"{title}. "
            f"Genres: {', '.join(genres)}. "
            f"{synopsis}"
        )

        filtered_anime.append({
            "id": anime_id,
            "title": title,
            "genres": genres,
            "text": combined_text
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(filtered_anime, f, ensure_ascii=False, indent=2)

print(f"Saved {len(filtered_anime)} anime entries")
