import re
import requests
from typing import Dict, Any, List

class RegexParser:
    def parse(self, url: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        regex_patterns = parameters.get("regex_patterns", [])

        extracted_data = []

        for pattern in regex_patterns:
            matches = re.findall(pattern, response.text)
            extracted_data.append({f"pattern_{regex_patterns.index(pattern)}": matches})

        return extracted_data
