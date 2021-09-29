from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from FiScrape.spiders.FtSpider  import FtSpider
from FiScrape.spiders.InsiderSpider import InsiderSpider
from FiScrape.spiders.WsjSpider import WsjSpider
from FiScrape.search import query, start_date

process = CrawlerProcess(get_project_settings())
process.crawl(FtSpider)
# process.crawl(WsjSpider)
# process.crawl(InsiderSpider)
process.start()