import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.load_secets import (
    APP_ENV,
    PARENTSQUARE_USERNAME,
    PARENTSQUARE_PASSWORD,
    DATA_DIRECTORY,
    OUTPUT_DIRECTORY
)
from app.scraper.feed_scraper import FeedScraper
from app.processor.openai_processor import OpenAIProcessor
from app.generator.document_generator import DocumentGenerator
from app.utils.logger import logger

def initialize_components():
    logger.info("Initializing components...")
    scraper = FeedScraper()
    openai_proc = OpenAIProcessor()
    doc_gen = DocumentGenerator(OUTPUT_DIRECTORY)
    return scraper, openai_proc, doc_gen

def collect_feeds(scraper):
    logger.info("Logging into ParentSquare and collecting feeds...")
    scraper.login()
    feeds = scraper.fetch_all_feeds()
    scraper.close()
    logger.info(f"Collected {len(feeds)} feeds.")
    return feeds

def extract_topics_from_feeds(openai_proc, feeds):
    logger.info("Extracting topics from collected feeds...")
    all_text = "\n".join([f["content"] for f in feeds])
    topics_json = openai_proc.extract_topics(all_text)
    logger.info("Extracted topics: %s", topics_json)
    return topics_json

def generate_material(doc_gen, topics_json):
    logger.info("Generating weekly study material...")
    doc_gen.generate_week_material(topics_json)
    logger.info("Material generation complete.")

def main():
    scraper, openai_proc, doc_gen = initialize_components()
    feeds = collect_feeds(scraper)
    topics_json = extract_topics_from_feeds(openai_proc, feeds)
    generate_material(doc_gen, topics_json)

if __name__ == "__main__":
    main()