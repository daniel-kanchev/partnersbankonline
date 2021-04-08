import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from partnersbankonline.items import Article


class partnersbankonlineSpider(scrapy.Spider):
    name = 'partnersbankonline'
    start_urls = ['https://www.partnersbankonline.com/blog/']

    def parse(self, response):
        links = response.xpath('//a[@class="post__title"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h3[@class="interior-subtitle"]/text()').get()
        if date:
            date = " ".join(date.split()[2:5])

        content = response.xpath('//div[@class="site-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
