import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig


class ExtractionService:
    @staticmethod
    async def extract_website(url):
        """Extract content from a website and return it as markdown."""
        crawler_run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=crawler_run_config)
            return result.markdown