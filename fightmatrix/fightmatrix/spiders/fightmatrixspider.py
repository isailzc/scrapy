import scrapy
from fightmatrix.items import FightmatrixItem

class FightmatrixspiderSpider(scrapy.Spider):
    name = "fightmatrixspider"
    allowed_domains = ["www.fightmatrix.com", "fightmatrix.com", "www.sherdog.com", "sherdog.com"]
    start_urls = []

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]

    sherdog_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    def parse(self, response):
        fighters = response.xpath("//td[contains(@onmouseover, 'LoadCustomData')]/a[@target='_blank']/@href").getall()

        for fighter in fighters:
            # Corregida la indentación del yield para que procese todos los peleadores, no solo el último
            yield response.follow(fighter, callback=self.parse_fighter_page)

    def parse_fighter_page(self, response):
        matrix_item = FightmatrixItem()
        matrix_item['fighter'] = response.xpath("//h1[contains(@class, 'entry-title')]/a/text()").get()
        matrix_item['birthd'] = response.xpath("//div[contains(text(), 'Birth Date: ')]/strong/text()").get()
        matrix_item['prorecord'] = response.xpath('//div[contains(text(), "Pro Record:")]/strong/text()').get()
        matrix_item['ufcdebut'] = response.xpath("//div[contains(text(), 'UFC Debut:')]/strong/text()").get()
        matrix_item['ufcrecord'] = response.xpath('//a[contains(text(), "UFC Record")]/following-sibling::strong/text()').get()
        matrix_item['oct_time'] = response.xpath('//a[contains(text(), "Octagon Time")]/following-sibling::strong/text()').get()
        matrix_item['longest_ws'] = response.xpath('//a[contains(text(), "Longest Win Streak")]/following-sibling::strong/text()').get()
        matrix_item['last_ufc_fight'] = response.xpath('//div[contains(text(), "Last UFC Fight: ")]/strong/text()').get()
        matrix_item['last_5'] = response.xpath("//div[contains(text(), 'Last 5: ')]/span/text()").getall()
        matrix_item['association'] = response.xpath("//div[contains(text(), 'Association: ')]/strong/text()").get()
        matrix_item['pro_d_date'] = response.xpath("//div[contains(text(), 'Pro Debut Date: ')]/strong/text()").get()

        # Extraemos el enlace hacia el perfil de Sherdog
        sherdog_url = response.xpath("//a[contains(@href, 'sherdog.com/fighter/')]/@href").get()

        if sherdog_url:
            # Hacemos la petición a Sherdog pasando los headers y el item en construcción
            yield scrapy.Request(
                url=sherdog_url,
                headers=self.sherdog_headers,
                callback=self.parse_sherdog_page,
                cb_kwargs={'item': matrix_item}
            )
        else:
            # Si un peleador no tiene enlace a Sherdog, devolvemos lo que tenemos
            yield matrix_item

    def parse_sherdog_page(self, response, item):
        # Datos biográficos y físicos
        item['sherdog_age'] = response.xpath("//div[contains(@class, 'bio-holder')]//td/b/text()").get()
        item['sherdog_birthdate'] = response.xpath("//span[@itemprop='birthDate']/text()").get()
        item['sherdog_division'] = response.xpath("//div[contains(@class, 'association-class')]/a/text()").get()
        
        height_raw = response.xpath('//b[@itemprop="height"]/following-sibling::em/following-sibling::text()').get()
        item['sherdog_height_cm'] = height_raw.strip() if height_raw else None

        # Historial de las últimas 5 peleas
        # En lugar de extraer los datos en listas separadas y arriesgarnos a que se desfasen,
        # iteramos por cada fila (row) para mantener los datos de cada pelea perfectamente agrupados.
        fights = []
        # Busca cualquier contenedor con la clase 'fight_history' y extrae las filas con datos (<tr> que contengan <td>)
        rows = response.xpath("//*[contains(@class, 'fight_history')]//tr[td]")[1:6]
        
        for row in rows:
            fight = {
                'result': row.xpath(".//span[contains(@class, 'final_result')]/text()").get(),
                'opponent': row.xpath(".//a[contains(@href, '/fighter/')]/text()").get(),
                'event': "".join(row.xpath(".//a[contains(@href, '/events/')]//text()").getall()).strip(),
                'date': row.xpath(".//span[@class='sub_line']/text()").get(),
                'method': row.xpath(".//td[contains(@class, 'winby')]/b/text()").get(),
                'round': row.xpath(".//td[contains(@class, 'winby')]/following-sibling::td[1]/text()").get(),
                'time': row.xpath(".//td[contains(@class, 'winby')]/following-sibling::td[2]/text()").get()
            }
            fights.append(fight)
        
        item['sherdog_recent_fights'] = fights

        yield item