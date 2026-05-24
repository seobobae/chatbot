import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY")

def google_ai_mode_search(query: str) -> str:
    payload = {
        "engine": "google_ai_mode",
        "q": query,
        "api_key": API_KEY
    }

    try:
        response = requests.get("https://serpapi.com/search", params=payload)
        response.raise_for_status()
        data = response.json()

        # reconstructed_markdown에서 결과 추출
        result = data.get("reconstructed_markdown", "")
        if not result:
            # text_blocks에서 fallback
            blocks = data.get("text_blocks", [])
            result = "\n".join(
                block.get("snippet", "")
                for block in blocks
                if block.get("type") == "paragraph"
            )

        if not result:
            return "검색 결과를 찾을 수 없습니다."

        return result

    except Exception as e:
        return f"오류 발생: {str(e)}"