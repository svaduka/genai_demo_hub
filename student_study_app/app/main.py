from app.config.config_loader import ConfigLoader
from app.scraper.feed_scraper import FeedScraper
from app.processor.openai_processor import OpenAIProcessor
from app.generator.document_generator import DocumentGenerator
from app.utils.logger import logger

def main():
    config = ConfigLoader().config
    scraper = FeedScraper(config)
    scraper.login()
    feeds = scraper.fetch_all_feeds()
    scraper.close()

    all_text = "\n".join([f["content"] for f in feeds])

    openai_proc = OpenAIProcessor(config['openai']['api_key'])
    topics_json = openai_proc.extract_topics(all_text)
    logger.info("Extracted topics: %s", topics_json)

    doc_gen = DocumentGenerator(config['output']['folder'])
    doc_gen.generate_week_material(eval(topics_json))

if __name__ == "__main__":
    main()