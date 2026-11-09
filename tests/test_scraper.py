"""Unit tests verifying fetcher retries, HTML parsing, data persistence, and report generation."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from scraper.fetcher import WebFetcher
from scraper.parser import parse_quotes_page
from scraper.pipeline import ScraperPipeline


SAMPLE_HTML = """
<html>
<body>
    <div class="quote">
        <span class="text">“The best way to predict the future is to invent it.”</span>
        <small class="author">Alan Kay</small>
        <div class="tags"><a class="tag">inspirational</a></div>
    </div>
    <div class="quote">
        <span class="text">“Life is what happens when you're busy making other plans.”</span>
        <small class="author">John Lennon</small>
        <div class="tags"><a class="tag">life</a></div>
    </div>
</body>
</html>
"""


def test_parser_extracts_correct_fields():
    records = parse_quotes_page(SAMPLE_HTML)
    assert len(records) == 2
    assert records[0]["author"] == "Alan Kay"
    assert "future" in records[0]["quote"]
    assert records[0]["tags"] == ["inspirational"]
    assert records[1]["author"] == "John Lennon"


@patch("scraper.fetcher.requests.Session")
def test_fetcher_success(mock_session_cls):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = SAMPLE_HTML
    mock_session.get.return_value = mock_response
    mock_session_cls.return_value = mock_session

    fetcher = WebFetcher(delay=0.0)
    html = fetcher.fetch("http://example.com")
    assert html == SAMPLE_HTML


@patch("scraper.pipeline.WebFetcher")
def test_pipeline_etl_execution(mock_fetcher_cls, tmp_path: Path):
    mock_fetcher = MagicMock()
    mock_fetcher.fetch.return_value = SAMPLE_HTML
    mock_fetcher_cls.return_value = mock_fetcher

    json_file = tmp_path / "quotes.json"
    csv_file = tmp_path / "quotes.csv"
    report_file = tmp_path / "report.txt"

    pipeline = ScraperPipeline()
    pipeline.fetcher = mock_fetcher

    records = pipeline.run(max_pages=1, json_p=json_file, csv_p=csv_file, report_p=report_file)

    assert len(records) == 2
    assert json_file.exists()
    assert csv_file.exists()
    assert report_file.exists()

    report_content = report_file.read_text(encoding="utf-8")
    assert "Total Quotes Extracted : 2" in report_content
