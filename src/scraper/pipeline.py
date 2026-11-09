"""ETL Pipeline orchestrating scraping, transformation, persistence, and summary reporting."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from scraper.fetcher import WebFetcher
from scraper.parser import parse_quotes_page


class ScraperPipeline:
    """Orchestrates extraction from quotes.toscrape.com, transformation, CSV/JSON save, and statistics report."""

    def __init__(self, base_url: str = "http://quotes.toscrape.com/page/") -> None:
        self.base_url = base_url
        self.fetcher = WebFetcher(delay=0.1)

    def extract_pages(self, max_pages: int = 3) -> List[Dict[str, Any]]:
        all_records: List[Dict[str, Any]] = []
        for page_num in range(1, max_pages + 1):
            url = f"{self.base_url}{page_num}/"
            html = self.fetcher.fetch(url)
            if html:
                records = parse_quotes_page(html)
                if not records:
                    break
                all_records.extend(records)
            else:
                break
        return all_records

    def save_data(self, records: List[Dict[str, Any]], json_path: Path, csv_path: Path) -> None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_path.write_text(json.dumps({"total_records": len(records), "quotes": records}, indent=2, sort_keys=True), encoding="utf-8")

        # Save CSV
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["author", "length", "quote", "tags"])
            writer.writeheader()
            for r in records:
                row = r.copy()
                row["tags"] = ", ".join(row["tags"])
                writer.writerow(row)

    def generate_summary_report(self, records: List[Dict[str, Any]], report_path: Path) -> str:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        total = len(records)
        authors = set(r["author"] for r in records)
        avg_len = round(sum(r["length"] for r in records) / total, 2) if total > 0 else 0.0

        report_lines = [
            "=" * 50,
            "WEB SCRAPING & DATA EXTRACTION SUMMARY REPORT",
            "=" * 50,
            f"Total Quotes Extracted : {total}",
            f"Unique Authors Found   : {len(authors)}",
            f"Average Quote Length   : {avg_len} characters",
            "=" * 50,
        ]
        report_text = "\n".join(report_lines)
        report_path.write_text(report_text, encoding="utf-8")
        return report_text

    def run(self, max_pages: int = 3, json_p: Path = Path("data/scraped_quotes.json"), csv_p: Path = Path("data/scraped_quotes.csv"), report_p: Path = Path("reports/summary_report.txt")) -> List[Dict[str, Any]]:
        records = self.extract_pages(max_pages=max_pages)
        if records:
            self.save_data(records, json_p, csv_p)
            self.generate_summary_report(records, report_p)
        return records
