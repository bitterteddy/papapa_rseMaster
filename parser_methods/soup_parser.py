import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class SoupParser:
    def parse(self, url: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        container_selector = parameters.get("container_selector")
        containers = soup.select(container_selector) if container_selector else []

        extracted_data = []

        for container in containers:
            item_data = {}

            for element in parameters.get("elements", []):
                selector = element.get("selector")
                attribute = element.get("attribute", "text")
                name = element.get("name")
                multiple = element.get("multiple", False)

                if multiple:
                    extracted_elements = [
                        match.get(attribute, None) if attribute != "text" else match.get_text(strip=True)
                        for match in container.select(selector)
                    ]
                    item_data[name] = extracted_elements
                else:
                    match = container.select_one(selector)
                    item_data[name] = match.get(attribute, None) if attribute != "text" and match else (
                        match.get_text(strip=True) if match else None
                    )

            extracted_data.append(item_data)

        return extracted_data
