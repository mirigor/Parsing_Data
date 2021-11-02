import scrapy


def price_data(response):
    """Сбор информации об обычной-цене товара"""

    if response.css('.nA .nF span::text').extract_first() == 'Нет в наличии':
        return
    else:
        if response.css('.Cd.Ch .Ce').extract():
            original_price = response.css('.Cd .Cf .Cg::text').extract_first()
        else:
            original_price = response.css('.Cd .Ce::text').extract_first()
        temp = ''
        for x in str(original_price):
            if x.isdigit() or x == '.':
                temp += x
        original_price = float(temp)
        return round(original_price)


def promo_price_data(response):
    """Сбор информации о промо-цене товара"""

    if response.css('.nA .nF span::text').extract_first() == 'Нет в наличии' or not response.css('.Cd.Ch .Ce::text').extract_first():
        return
    else:
        price = response.css('.Cd.Ch .Ce::text').extract_first()
        temp = ''
        for x in str(price):
            if x.isdigit() or x == '.':
                temp += x
        price = float(temp)
        return round(price)


class CatalogSpider(scrapy.Spider):
    name = 'catalog'
    allowed_domains = ['detmir.ru']
    start_urls = [f'https://www.detmir.ru/catalog/index/name/lego']

    def parse(self, response, **kwargs):
        for page in range(2, 100):
            if response.css('.Ma.MC::attr("href")').extract():
                for href in response.css('.Ma.MC::attr("href")').extract():
                    url = response.urljoin(href)
                    yield scrapy.Request(url, callback=self.parsing_data)

                next_page_url = f'https://www.detmir.ru/catalog/index/name/lego/page/{page}/'
                next_page_url = response.urljoin(next_page_url)
                yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parsing_data(response):
        item = {
            'id': response.css('div::attr(data-product-id)').extract_first(),
            "title": response.css('.qX .qZ.q_::text').extract_first(),
            "price": price_data(response),
            "promo_price": promo_price_data(response),
            'url': response.request.url,
        }
        yield item
