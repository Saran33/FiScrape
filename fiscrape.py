from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from FiScrape.spiders.FtSpider  import FtSpider
from FiScrape.spiders.InsiderSpider import InsiderSpider
from FiScrape.spiders.BBCSpider import BBCSpider
# from FiScrape.spiders.WsjSpider import WsjSpider
from FiScrape.spiders.ZhSpider import ZhSpider
from FiScrape.search import query, start_date

# scrapy runspider fiscrape.py
# python3 fiscrape.py

process = CrawlerProcess(get_project_settings())
process.crawl(FtSpider)
# process.crawl(WsjSpider)
process.crawl(InsiderSpider)
process.crawl(BBCSpider)
process.crawl(ZhSpider)
process.start()


# setting = get_project_settings()
# process = CrawlerProcess(setting)

# for spider_name in process.spiders.list():
#     print ("Running spider %s" % (spider_name))
#     process.crawl(spider_name,query="dvh") #query dvh is custom argument used in your scrapy

# process.start()


# # OR via shell script:
# scrapy runspider ft &
# scrapy runspider insider  &
# scrapy runspider bbc

# chmod +x script_name

# # To schedule a cronjob every 6 hours:
# crontab -e
# * */6 * * * path/to/shell/script_name >> path/to/file.log