import random
import re
import requests
from bs4 import BeautifulSoup
import config

from .base import BaseCrawler
from utils.logger import get_logger

logger = get_logger("cryptotradingcafe", log_file="logs/cryptotradingcafe.log")


class CryptoTradingCafeCrawler(BaseCrawler):
    def __init__(self, user_agents, mongo_storage):
        super().__init__(user_agents)
        self.mongo_storage = mongo_storage
        self.batch_id = config.BATCH_ID
        self.urls_has_craw = set(
            mongo_storage.get_start_config("cryptotradingcafe").get("url", [])
            if mongo_storage.get_start_config("cryptotradingcafe") else []
        )
        logger.info(f"已加载 {len(self.urls_has_craw)} 条历史链接")

    def article_get(self, url):
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Referer": "https://www.cryptotradingcafe.com/",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.find_all(class_=re.compile('site-main'))

            title = elements[0].find(class_=re.compile("entry-title")).text.strip()
            author = ""
            create_time = elements[0].find(class_=re.compile('entry-meta')).text.strip()
            create_time = create_time.replace("年", " ").replace("月", " ").replace("日", "")
            content = re.sub(r'请给本文评分.*$', "",
                             elements[0].find(class_=re.compile('entry-content clear')).text.strip(),
                             flags=re.DOTALL)

            logger.info(f"成功解析文章：{title}")
            return {
                "status_code": response.status_code,
                "title": title,
                "author": author,
                "create_time": create_time,
                "content": content,
                "url": url,
                "batchId": self.batch_id
            }
        except Exception as e:
            logger.exception(f"解析文章失败：{url}")
            return {}

    def crawl(self):
        page = 1
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Referer": "https://www.cryptotradingcafe.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        logger.info("开始爬取 CryptoTradingCafe")

        while True:
            hrefs = set()
            page_url = f'https://cryptotradingcafe.com/page/{page}'
            try:
                logger.info(f"请求页面：{page_url}")
                response = requests.get(page_url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
                elements = soup.find_all(class_=re.compile('entry-title ast-blog-single-element'))

                for block in elements:
                    a_tag = block.find('a', href=True)
                    if a_tag:
                        hrefs.add(a_tag['href'])

                if not (hrefs - self.urls_has_craw):
                    logger.info("所有链接都已爬取，终止爬取。")
                    break

                for url in hrefs:
                    if url in self.urls_has_craw:
                        continue
                    self.urls_has_craw.add(url)
                    data = self.article_get(url)
                    if not data:
                        logger.warning(f"爬取失败，记录错误：{url}")
                        self.mongo_storage.insert("error_log", {
                            "source": "cryptotradingcafe",
                            "url": url,
                            "batchId": self.batch_id
                        })
                    else:
                        self.mongo_storage.insert("source_data_cryptotradingcafe", data)

            except Exception as e:
                logger.exception(f"请求页面失败：{page_url}")

            page += 1

        # 最后更新已爬取链接记录
        self.mongo_storage.update_one(
            {"_id": "cryptotradingcafe"},
            {"url": list(self.urls_has_craw)}
        )
        logger.info("爬取任务完成")
