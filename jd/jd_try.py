import json
import requests
from time import sleep
from lxml import etree
from bs4 import BeautifulSoup
import pymongo
from urllib import parse
from os.path import abspath, dirname

TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'


class JDTry(object):
    def __init__(self):
        self.url = "https://try.jd.com/activity/getActivityList?page="
        self.url_applycount = 'https://try.jd.com/public/getApplyCountByActivityIds?activityIds='
        self.url_skuprice = 'https://p.3.cn/prices/mgets?'
        self.session = requests.Session()
        self.referer_url = 'try.jd.com'
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client.jingdong  # 数据库名
        self.collection_skus = self.db.tryskus  # sku信息
        self.collection_skus.create_index('sku_id', unique=True)

    def ajax_get_applycount(self, apply_ids):
        """
        获取商品申请人数
        :param apply_ids:
        :return:
        """
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'try.jd.com',
            'Referer': self.referer_url,
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36',
        }
        url = self.url_applycount + apply_ids
        self.session.headers.update(headers)
        response = self.session.get(url)
        if response.status_code == 200:
            print('*' * 40)
            print(type(response.text))
            print(type(json.loads(response.text)))
            print(json.loads(response.text))
            return json.loads(response.text)
        else:
            return None

    def ajax_get_skuprice(self, skuids):
        """
                获取商品申请人数
                :param apply_ids:
                :return:
                """
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.referer_url,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36',
        }
        query = {
            'type': 1,
            'skuIds': skuids
        }
        url = self.url_skuprice + parse.urlencode(query)
        # self.session.headers.update(headers)
        # response = self.session.get(url)
        response = requests.get(url, headers=headers, allow_redirects=False)
        if response.status_code == 200:
            print('*'*40)
            print(type(response.text))
            print(type(json.loads(response.text)))
            print(json.loads(response.text))
            return json.loads(response.text)
        else:
            return None

    def save_to_mongodb(self):
        pass

    def parse_item_by_bs4(self, res):
        """
        bs4解析数据
        :param res:
        :return:
        """
        soup = BeautifulSoup(res, 'lxml')
        apply_ids = []
        sku_ids = []
        data_list = []
        items = soup.select('#goods-list .clearfix .item')

        for item in items:
            data = {
                'sku_id': item['sku_id'],
                'activity_id': item['activity_id'],
                'img': item.select('.p-img img')[0]['src'],
                'name': item.select('.p-name')[0].get_text(),
                'supply': item.select('.t1 b')[0].get_text(),
                'apply_count': '0',  # ajax获取
                'price': '0',  # 调用接口 https://p.3.cn/prices/mgets?skuIds=J_52844652747,J_&type=1
                'link': item.select('.link')[0]['href']
            }
            sku_ids.append(item['sku_id'])
            apply_ids.append(item['activity_id'])
            data_list.append(data)

        # print(sku_ids, apply_ids)

        return apply_ids, data_list, sku_ids

    def parse_item_by_pq(self, res):
        # pq解析数据
        pass

    def parse_item_by_xpath(self, text):
        pass

    def get_page(self, offset):

        # 构造headers
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'try.jd.com',
            'Referer': self.referer_url,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36',
        }
        url = self.url + str(offset)
        print(headers)
        self.session.headers.update(headers)
        response = self.session.get(url)
        if response.status_code == 200:
            self.referer_url = url
            sleep(1)
            # 解析一些数据
            apply_ids, data_list, sku_ids = self.parse_item_by_bs4(response.text)

            # 获取到产品ID集，作为参数通过ajax获取已申请数的数据

            applycounts = self.ajax_get_applycount(','.join(apply_ids))     # 返回json数据
            skus_price = self.ajax_get_skuprice(','.join(sku_ids))    # 返回json数据

            # 将数据补充完整
            if applycounts is not None and skus_price is not None:
                for data in data_list:
                    activity_id = data['activity_id']
                    sku_id = data['sku_id']
                    for index in range(0, len(applycounts)):
                        if activity_id == str(applycounts[index]['activity_id']):
                            data['apply_count'] = str(applycounts[index]['count'])
                    for index in range(0, len(skus_price)):
                        if sku_id == skus_price[index]['id'].replace('J_', ''):  # 'J_52844652747'
                            data['price'] = skus_price[index]['p']
                    print(data)
                    print('=' * 20)

                    # 保存至Mongo数据库
                    if not self.collection_skus.find_one({'sku_id': data['sku_id']}):
                        self.collection_skus.insert_one(data)



    def main(self):
        self.get_page(1)


if __name__ == '__main__':
    jd_try = JDTry()
    jd_try.main()

