import random
import re
import time
import requests
from bs4 import BeautifulSoup
import config
from functools import wraps

from .base import BaseCrawler
from utils.logger import get_logger

logger = get_logger("jmtt", log_file="logs/jmtt.log")

# 重试装饰器
def retry(times=3, delay=3, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"{func.__name__}第{attempt+1}次失败: {e}")
                    if attempt < times - 1:
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__}重试{times}次失败，放弃。")
                        raise
        return wrapper
    return decorator


class JMTTCrawler(BaseCrawler):
    def __init__(self, user_agents, mongo_storage):
        super().__init__(user_agents)
        self.mongo_storage = mongo_storage
        self.batch_id = config.BATCH_ID
        self.urls_has_craw = mongo_storage.get_start_config("jmtt") or {}

        self.base_urls = {
            'cryptocurrency': 'https://2jmtt.com/cryptocurrency',
            'newbie': 'https://2jmtt.com/newbie',
            'dealings': 'https://2jmtt.com/dealings',
            'bitcoin': 'https://2jmtt.com/bitcoin',
            'chain': 'https://2jmtt.com/chain',
            'analysis': 'https://2jmtt.com/analysis',
            'drop': 'https://2jmtt.com/drop',
            'encyclopedia': 'https://2jmtt.com/encyclopedia',
            'ethereum': 'https://2jmtt.com/ethereum',
            'mining': 'https://2jmtt.com/mining',
            'renwu': 'https://2jmtt.com/renwu'
        }

    @retry(times=3, delay=3, exceptions=(requests.RequestException,))
    def get_urls(self, url, headers):
        root_url = "https://2jmtt.com"
        hrefs = []
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        elements = soup.find_all(class_=re.compile('t_newlist b icon'))
        if not elements:
            logger.warning(f"列表页结构异常，无内容: {url}")
            return []

        uls = elements[0].find_all('ul')
        for ul in uls:
            links = ul.find_all('a', href=True)
            for link in links:
                hrefs.append(root_url + link['href'])
        return hrefs

    @retry(times=3, delay=3, exceptions=(requests.RequestException,))
    def article_get(self, url, headers):
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(class_=re.compile('main'))
        if not elements:
            raise ValueError(f"文章结构异常: {url}")

        title = elements[0].find(class_=re.compile("art_tit cen")).text
        creators = elements[0].find(class_=re.compile('art_time cen')).find_all('span')
        if len(creators) < 2:
            raise ValueError(f"作者或时间缺失: {url}")
        author, create_time = creators[0].text.strip(), creators[1].text.strip()
        description = elements[0].find(class_=re.compile('art_desc')).text
        content = re.sub(r'下一篇.*$', "", elements[0].find(class_=re.compile('art_con')).text.strip(),
                         flags=re.DOTALL)

        logger.info(f"成功解析文章：{title}")
        return {
            "status_code": response.status_code,
            "title": title,
            "author": author,
            "create_time": create_time,
            "content": content,
            "url": url,
            "batchId": self.batch_id,
            "description": description
        }

    def crawl(self):
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Referer": "https://2jmtt.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        for base, base_url in self.base_urls.items():
            has_craw = set(self.urls_has_craw.get(base, []))
            logger.info("开始爬取" + base)
            page = 1
            while True:
                page_url = base_url
                if page != 1:
                    page_url += "/index_" + str(page) + ".html"

                try:
                    hrefs = set(self.get_urls(page_url, headers))
                except Exception as e:
                    logger.error(f"请求列表页失败，跳过此页: {page_url}，错误: {e}")
                    break

                new_links = hrefs - has_craw
                if not new_links:
                    logger.info("所有链接都已爬取，终止爬取。")
                    break

                for url in new_links:
                    try:
                        data = self.article_get(url, headers)
                    except Exception as e:
                        logger.error(f"文章请求失败，记录错误：{url}，错误: {e}")
                        self.mongo_storage.insert("error_log", {
                            "source": "jmtt",
                            "url": url,
                            "batchId": self.batch_id
                        })
                        continue

                    if not data:
                        logger.warning(f"爬取失败，记录错误：{url}")
                        self.mongo_storage.insert("error_log", {
                            "source": "jmtt",
                            "url": url,
                            "batchId": self.batch_id
                        })
                    else:
                        self.mongo_storage.insert("source_data_jmtt", data)
                        has_craw.add(url)

                # 每页结束更新已爬取链接记录
                self.mongo_storage.update_one({"_id": "jmtt"}, {base: list(has_craw)})
                page += 1

            logger.info(base + "爬取任务完成")
