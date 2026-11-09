"""HTML parser extracting structured quote records using BeautifulSoup."""

from typing import Any, Dict, List
from bs4 import BeautifulSoup


def parse_quotes_page(html_content: str) -> List[Dict[str, Any]]:
    """Parse quotes.toscrape.com HTML structure into clean structured dictionaries."""
    soup = BeautifulSoup(html_content, "html.parser")
    items = soup.select(".quote")
    parsed_records: List[Dict[str, Any]] = []

    for item in items:
        text_elem = item.select_one(".text")
        author_elem = item.select_one(".author")
        tag_elems = item.select(".tag")

        quote_text = text_elem.get_text(strip=True) if text_elem else ""
        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
        tags = [tag.get_text(strip=True) for tag in tag_elems]

        parsed_records.append({
            "quote": quote_text,
            "author": author,
            "tags": tags,
            "length": len(quote_text),
        })

    return parsed_records
