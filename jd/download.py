import pymongo
import aiohttp
import asyncio
from os.path import abspath, dirname

TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'


class DownLoad(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client.jingdong  # 数据库名
        self.collection_skus = self.db.tryskus  # sku信息

    async def __get_content(self, link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36'
        }
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=link, headers=headers)
            # print(response.text)
            content = await response.read()
            print(type(content))
            # print(content)
        return content

    async def __download_img(self, img):
        path = img.split('/')[-1]
        url = 'http:'+img
        # print(url)
        content = await self.__get_content(url)
        # print(type(content))
        # print(content)
        if content is not None:
            with open(TEMPLATES_FOLDER + path, 'wb') as f:
                f.write(content)
            print('下载图片成功')
        else:
            print(url, 'content is None')

    def run(self):
        """
        下载图片
        :return:
        """
        # 读取mongo数据库，获取img链接
        img_urls = self.collection_skus.find({}, {"_id": 0, "img": 1})   # 返回Cursor对象, 相当于生成器
        tasks = [asyncio.ensure_future(self.__download_img(url['img'])) for url in img_urls]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    download = DownLoad()
    download.run()
