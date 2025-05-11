import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.load_secets import (
    APP_ENV,
    OPENAI_API_KEY,
    PARENTSQUARE_USERNAME,
    PARENTSQUARE_PASSWORD,
    DATA_DIRECTORY,
    OUTPUT_DIRECTORY
)
from app.scraper.feed_scraper import FeedScraper
from openai import AsyncOpenAI
from app.processor.openai_processor import OpenAIProcessor
from app.generator.document_generator import DocumentGenerator
from app.utils.logger import logger

async def main():
    scraper = FeedScraper()
    scraper.login()
    feeds = scraper.fetch_all_feeds()
    scraper.close()

    all_text = "\n".join([f["content"] for f in feeds])

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    openai_proc = OpenAIProcessor(client)
    topics_json = await openai_proc.extract_topics(all_text, api_key=OPENAI_API_KEY)
    logger.info("Extracted topics: %s", topics_json)

    doc_gen = DocumentGenerator(OUTPUT_DIRECTORY)
    doc_gen.generate_week_material(topics_json)

if __name__ == "__main__":
    asyncio.run(main())