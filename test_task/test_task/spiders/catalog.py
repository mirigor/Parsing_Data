import scrapy


def price_data(response):
    """Сбор информации об обычной-цене товара"""

    if response.css('.nb .ng span::text').extract_first() == 'Нет в наличии':
        return
    else:
        if response.css('.B_8.Cc .B_9').extract():
            original_price = response.css('.B_8 .Ca .Cb::text').extract_first()
        else:
            original_price = response.css('.B_8 .B_9::text').extract_first()
        temp = ''
        for x in str(original_price):
            if x.isdigit() or x == '.':
                temp += x
        original_price = float(temp)
        return round(original_price)


def promo_price_data(response):
    """Сбор информации о промо-цене товара"""

    if response.css('.nb .ng span::text').extract_first() == 'Нет в наличии' or not response.css('.B_8.Cc .B_9::text').extract_first():
        return
    else:
        price = response.css('.B_8.Cc .B_9::text').extract_first()
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
            if response.css('.M_7.Nz::attr("href")').extract():
                for href in response.css('.M_7.Nz::attr("href")').extract():
                    url = response.urljoin(href)
                    yield scrapy.Request(url, callback=self.parsing_data)

                next_page_url = f'https://www.detmir.ru/catalog/index/name/lego/page/{page}/'
                next_page_url = response.urljoin(next_page_url)
                yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parsing_data(response):
        item = {
            'id': response.css('div::attr(data-product-id)').extract_first(),
            "title": response.css('.rW .rY.rZ::text').extract_first(),
            "price": price_data(response),
            "promo_price": promo_price_data(response),
            'url': response.request.url,
        }
        yield item
