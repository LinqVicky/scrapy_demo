# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from jdscrapy.items import JdscrapyItem

script = """
function main(splash, args)
  splash.images_enabled = false
  assert(splash:go(args.url))
  assert(splash:wait(args.wait))
  js = string.format("document.querySelector('#page_jump_num').value=%d;document.querySelector('a.btn.btn-default').click()", args.page)
  splash:evaljs(js)
  assert(splash:wait(args.wait))
  return splash:html()
end
"""
#js = string.format("document.querySelector('#page_jump_num').value=%d;document.querySelector('span.p-skip > a.btn').click(), args.page)


class JdtrySpider(scrapy.Spider):
    name = 'jdtry'
    allowed_domains = ['https://try.jd.com/']
    base_url = 'https://try.jd.com/activity/getActivityList'

    def start_requests(self):
        for page in range(1, self.settings.get('MAX_PAGE') + 1):
            yield SplashRequest(self.base_url, callback=self.parse, endpoint='execute', args={'lua_source': script,
                                                                                              'page': page, 'wait': 7})

    def parse(self, response):
        items = response.css('#goods-list .clearfix .item')
        for item in items:
            try_sku = JdscrapyItem()
            try_sku['sku_id'] = item.css('.item::attr(sku_id)').extract_first()
            try_sku['activity_id'] = item.css('.item::attr(activity_id)').extract_first()
            try_sku['img'] = item.css('.p-img img::attr(src)').extract_first()
            try_sku['name'] = item.css('.p-name::text').extract_first()
            try_sku['supply'] = item.css('.t1').xpath('./b/text()').extract_first()
            try_sku['apply_count'] = item.css('.t1 .b2::text').extract_first()
            try_sku['price'] = item.css('.p-price').xpath('./span/text()').extract_first()
            try_sku['link'] = item.css('.link::attr(href)').extract_first()
            yield try_sku
