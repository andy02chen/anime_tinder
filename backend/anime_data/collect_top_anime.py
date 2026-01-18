import os
import json
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import asyncio

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")

urls = ["https://api.myanimelist.net/v2/anime/ranking?ranking_type=all&limit=500&fields=genres%2Csynopsis",
"https://api.myanimelist.net/v2/anime/ranking?offset=500&ranking_type=all&limit=500&fields=genres%2Csynopsis",
"https://api.myanimelist.net/v2/anime/ranking?offset=1000&ranking_type=all&limit=500&fields=genres%2Csynopsis",
"https://api.myanimelist.net/v2/anime/ranking?offset=1500&ranking_type=all&limit=500&fields=genres%2Csynopsis",
"https://api.myanimelist.net/v2/anime/ranking?offset=2000&ranking_type=all&limit=500&fields=genres%2Csynopsis"]

async def collect_top_anime():
    headers = {
        "X-MAL-CLIENT-ID": f"{CLIENT_ID}"
    }
    all_anime = []

    async with httpx.AsyncClient() as client:
        for index, url in enumerate(urls, start=1):
          resp = await client.get(url, headers=headers)

          if resp.status_code != 200:
              raise HTTPException(status_code=resp.status_code, detail="Failed to fetch top anime from MyAnimeList")

          data = resp.json()
          anime_list = data.get("data", [])

          with open(f"top_anime_{index}.json", "w", encoding="utf-8") as f:
              json.dump(anime_list, f, ensure_ascii=False, indent=2)
          
    return "All files saved successfully"

if __name__ == "__main__":
    asyncio.run(collect_top_anime())