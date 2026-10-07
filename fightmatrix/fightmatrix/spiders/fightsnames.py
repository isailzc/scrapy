import scrapy


class FightsnamesSpider(scrapy.Spider):
    name = "fightsnames"
    allowed_domains = ["www.fightmatrix.com"]
    start_urls = []

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]

    def parse(self, response):
        # Extraer y limpiar nombres de peleadores
        peleadores_raw = response.xpath(
            "//table[@class='tblRank']//td[@class='tdRank']//strong/text()"
        ).getall()
        
        peleadores = [p.strip() for p in peleadores_raw if p.strip()]

        # Generar matchups en parejas
        for fighter_1, fighter_2 in zip(peleadores[::2], peleadores[1::2]):
            yield {
                'matchup': f"{fighter_1} vs {fighter_2}"
            }

