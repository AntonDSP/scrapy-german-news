# -*- coding: utf-8 -*-
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request

from crawler.items import CrawlerItem
from crawler.utils import get_first

class FocusSpider(CrawlSpider):
    name = 'focus'
    rotate_user_agent = True
    allowed_domains = ['www.focus.de']
    start_urls = ['http://www.focus.de']
    rules = (
        Rule(
            LinkExtractor(
                allow=('(politik|wirtschaft|panorama)',),
                deny=('\.html')
            ),
            follow=True
        ),
        Rule(
            LinkExtractor(
                allow=('(politik|wirtschaft)(\/\w+)*.*\.html'),
            ),
            callback='parse_page',
        ),
    )

    def parse_page(self, response):
        item = CrawlerItem()
        item['url'] = response.url.encode('utf-8')
        item['visited'] = datetime.datetime.now().isoformat().encode('utf-8')
        item['published'] = get_first(response.selector.xpath('//meta[@name="date"]/@content').extract())
        item['title'] = get_first(response.selector.xpath('//meta[@property="og:title"]/@content').extract())
        item['description'] = get_first(response.selector.xpath('//meta[@name="description"]/@content').extract())
        item['text'] = "".join([s.strip().encode('utf-8') for s in response.selector.css('.articleContent').xpath('.//div[@class="textBlock"]/p/text()').extract()])
        item['author'] = [s.encode('utf-8') for s in response.selector.xpath('//a[@rel="author"]/text()').extract()]
        item['keywords'] = [s.encode('utf-8') for s in response.selector.xpath('//meta[@name="keywords"]/@content').extract()]
        return item
