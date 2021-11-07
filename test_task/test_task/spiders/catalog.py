import scrapy


def price_data(response):
    """Сбор информации об обычной-цене товара"""

    if response.xpath("//aside/div/div/div/div/div/span/text()").extract_first() == 'Нет в наличии':
        return
    else:
        if response.xpath("//aside/div/div/div/div/div/div/div/div/span/text()").extract():
            original_price = response.xpath("//aside/div/div/div/div/div/div/div/div/span/text()").extract()[1]
        else:
            original_price = response.xpath("//aside/div/div/div/div/div/div/div/text()").extract_first()
        temp = ''
        for x in str(original_price):
            if x.isdigit() or x == '.':
                temp += x
        original_price = float(temp)
        return round(original_price)


def promo_price_data(response):
    """Сбор информации о промо-цене товара"""

    if response.xpath("//aside/div/div/div/div/div/span/text()").extract_first() == 'Нет в наличии' or not response.xpath("//aside/div/div/div/div/div/div/div/div/span/text()").extract():
        return
    else:
        price = response.xpath("//aside/div/div/div/div/div/div/div/text()").extract_first()
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
            if response.xpath("//div/div/div/div/div/div/div/div/div/div/div/div/a/@href").extract()[29:]:
                for href in response.xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/a/@href").extract():
                    url = response.urljoin(href)
                    yield scrapy.Request(url, callback=self.parsing_data)

                next_page_url = f'https://www.detmir.ru/catalog/index/name/lego/page/{page}/'
                next_page_url = response.urljoin(next_page_url)
                yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parsing_data(response):
        item = {
            'id': response.css('div::attr(data-product-id)').extract_first(),
            "title": response.xpath("//header/h1/text()").extract_first(),
            "price": price_data(response),
            "promo_price": promo_price_data(response),
            'url': response.request.url,
        }
        yield item
