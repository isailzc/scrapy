import scrapy


class TftspiderSpider(scrapy.Spider):
    name = "tftspider"
    allowed_domains = ["tactics.tools"]
    start_urls = ["https://tactics.tools/info/set-update"]

    def parse(self, response):
        champs = response.css('div.rounded.flex.flex')

        for champ in champs:
            yield{
                'name' : champ.css('div div::text').get()
            }
