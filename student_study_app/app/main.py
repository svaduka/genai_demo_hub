import logging
import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from app.utils.load_secets import (
    APP_ENV,
    PARENTSQUARE_USERNAME,
    PARENTSQUARE_PASSWORD,
    DATA_DIRECTORY,
    OUTPUT_DIRECTORY,
    CURRENT_GRADE
)
from app.scraper.feed_scraper import FeedScraper
from app.processor.openai_processor import OpenAIProcessor
from app.generator.document_generator import DocumentGenerator
from app.utils.logger import logger
from app.utils.logger import log_msg

import json

def read_feeds():
    output_dir = Path(__file__).resolve().parent.parent / "output"
    filepath = os.path.join(output_dir, "feeds.json")
    log_msg(f"Reading feeds from {filepath}", level=logging.INFO)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def initialize_components():
    log_msg("Initializing components...", level=logging.INFO)
    # scraper = FeedScraper()
    scraper = None
    openai_proc = OpenAIProcessor()
    doc_gen = DocumentGenerator(OUTPUT_DIRECTORY)
    return scraper, openai_proc, doc_gen

def collect_feeds(scraper):
    log_msg("Logging into ParentSquare and collecting feeds...", level=logging.INFO)
    scraper.login()
    feeds = scraper.fetch_all_feeds()
    scraper.close()
    log_msg(f"Collected {len(feeds)} feeds.", level=logging.INFO)
    return feeds


def generate_material(doc_gen, openai_proc, feeds):
    log_msg("Generating weekly study material from raw feeds...", level=logging.INFO)
    doc_gen.generate_week_material(openai_proc, feeds,CURRENT_GRADE)
    log_msg("Material generation complete.", level=logging.INFO)

def main():
    scraper, openai_proc, doc_gen = initialize_components()
    # feeds = collect_feeds(scraper)
    feeds = read_feeds()
    generate_material(doc_gen, openai_proc, feeds)

if __name__ == "__main__":
    main()