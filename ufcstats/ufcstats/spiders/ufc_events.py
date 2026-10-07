import scrapy


class UfcEventsSpider(scrapy.Spider):
    name = "ufc_events"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["https://ufcstats.com"]

    def parse(self, response):
        pass
