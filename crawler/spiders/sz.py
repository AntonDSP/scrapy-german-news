# -*- coding: utf-8 -*-
import datetime
import hashlib
import dateutil.parser as parser

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request

from crawler.items import CrawlerItem
from crawler.utils import get_first

class SZSpider(CrawlSpider):
    """Spider for 'Sueddeutsche Zeitung'"""
    name = 'sz'
    rotate_user_agent = True
    allowed_domains = ['www.sueddeutsche.de']
    start_urls = [
            'http://www.sueddeutsche.de',
            'http://www.sueddeutsche.de/thema',
    ]
    rules = (
        Rule(
            LinkExtractor(
                allow=('(politik|wirtschaft|panorama|thema)\/.+$',),
                deny=('\.\d+','news')
            ),
            follow=True
        ),
        Rule(
            LinkExtractor(
                allow=('(politik|wirtschaft|panorama)(\/\w+)*.*\.\d+$'),
            ),
            callback='parse_page',
        ),
    )

    def parse_page(self, response):
        """Scrapes information from pages into items"""
        item = CrawlerItem()
        item['url'] = response.url.encode('utf-8')
        item['visited'] = datetime.datetime.now().isoformat().encode('utf-8')
        item['published'] = parser.parse(get_first(response.selector.xpath('//time/@datetime').extract())).isoformat().encode('utf-8')
        item['title'] = get_first(response.selector.xpath('//meta[@property="og:title"]/@content').extract())
        item['description'] = get_first(response.selector.xpath('//meta[@name="description"]/@content').extract())
        item['text'] = "".join([s.strip().encode('utf-8') for s in response.selector.css('.article>.body>p').xpath('.//text()').extract()])
        item['author'] = [s.encode('utf-8') for s in response.selector.css('.authorContainer').xpath('.//span/strong/span/text()').extract()]
        item['keywords'] = [s.encode('utf-8') for s in response.selector.xpath('//meta[@name="news_keywords"]/@content').extract()]
        item['resource'] = self.name
        item['publication_id'] = hashlib.sha1((str(item['url']) + str(item['published']))).hexdigest()
        return item
