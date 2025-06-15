import random
import re
import requests
from bs4 import BeautifulSoup

import config
from .base import BaseCrawler
from utils.logger import get_logger

logger = get_logger("theblockbeats", log_file="logs/theblockbeats.log")


class TheBlockBeatsCrawler(BaseCrawler):
    def __init__(self, user_agents, mongo_storage):
        super().__init__(user_agents)
        self.mongo_storage = mongo_storage
        self.batch_id = config.BATCH_ID
        self.start_ids = self.get_start_ids()

    def get_start_ids(self):
        config = self.mongo_storage.get_start_config("theblockbeats")
        if config:
            flash_id = int(config.get("flash_last_number", 58000))
            news_id = int(config.get("news_last_number", 296000))
        else:
            flash_id = 58000
            news_id = 296000
        return {"flash": flash_id, "news": news_id}

    def extract_dates(self, s):
        # 从字符串中解析出时间
        # 匹配日期，可能带时间，也可能只有日期
        pattern = r'\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?'
        match = re.search(pattern, s)
        if match:
            return match.group()
        return ""

    def get_article(self, category, article_id):
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Referer": "https://www.theblockbeats.info/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        url = f"https://www.theblockbeats.info/{category}/{article_id}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"[theblockbeats] {url} 返回状态码 {response.status_code}")
                return None
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            if category == "news":
                elements = soup.find_all(class_=re.compile('contain-lft'))
                if not elements:
                    logger.warning(f"[theblockbeats] {url} 页面结构异常，未找到内容主体")
                    return None

                article_title = elements[0].find(class_=re.compile("news-title"))
                author = elements[0].find(class_=re.compile('news-author'))
                create_time = self.extract_dates(elements[0].find(class_=re.compile('news-intro')).text)
                article_content = elements[0].find(class_=re.compile('news-content'))

                if not all([article_title, author, create_time, article_content]):
                    logger.warning(f"[theblockbeats] {url} 文章部分内容缺失")
                    return None

                content_text = re.sub(r'欢迎加入律动.*$', "", article_content.text, flags=re.DOTALL)

                return {
                    "url": url,
                    "title": article_title.text.strip(),
                    "author": author.text.strip(),
                    "create_time": create_time,
                    "content": content_text.strip(),
                    "batchId": self.batch_id,
                    "jobId": article_id,
                    "category": category
                }

            elif category == "flash":
                elements = soup.find_all(class_=re.compile('flash-top-border'))
                if not elements:
                    logger.warning(f"[theblockbeats] {url} 页面结构异常，未找到flash内容主体")
                    return None

                article_title_el = elements[0].find(class_=re.compile("flash-title"))
                create_time_el = elements[0].find(class_=re.compile('item-time'))
                article_content_el = elements[0].find(class_=re.compile('flash-content'))

                if not all([article_title_el, create_time_el, article_content_el]):
                    logger.warning(f"[theblockbeats] {url} flash文章部分内容缺失")
                    return None

                return {
                    "url": url,
                    "title": article_title_el.text.strip(),
                    "author": "",  # flash栏目无作者信息，保持空字符串
                    "create_time": create_time_el.text.strip().replace("\t", "").replace("\n", ""),
                    "content": article_content_el.text.strip(),
                    "batchId": self.batch_id,
                    "jobId": article_id,
                    "category": category
                }
            else:
                logger.warning(f"[theblockbeats] 不支持的类别: {category}")
                return None

        except Exception as e:
            logger.exception(f"[theblockbeats] 请求或解析失败 {url}: {e}")
            return None

    def crawl_category(self, category, start_id):
        current_id = start_id
        success_ids = []
        fail_ids = []

        logger.info(f"[theblockbeats][{category}] 从ID {current_id} 开始爬取")

        while len(fail_ids) < config.MAX_WAIT_ARTICLES:
            article = self.get_article(category, current_id)
            if article:
                self.mongo_storage.insert("source_data_theblockbeats", article)
                success_ids.append(current_id)
                logger.info(f"[theblockbeats][{category}] 成功爬取文章ID {current_id}")
            else:
                fail_ids.append(current_id)
                logger.info(f"[theblockbeats][{category}] 文章ID {current_id} 爬取失败")
            current_id += 1

        logger.info(f"[theblockbeats][{category}] 进入重试阶段，失败ID数量 {len(fail_ids)}")

        retried_success_ids = []
        for _ in range(config.MAX_RETRIES):
            still_failed = []
            for fid in fail_ids:
                article = self.get_article(category, fid)
                if article:
                    self.mongo_storage.insert("source_data_theblockbeats", article)
                    retried_success_ids.append(fid)
                    logger.info(f"[theblockbeats][{category}] 重试成功文章ID {fid}")
                else:
                    still_failed.append(fid)
            fail_ids = still_failed
            if not fail_ids:
                break

        all_success = success_ids + retried_success_ids
        return all_success, fail_ids

    def crawl(self):
        flash_success, flash_fail = self.crawl_category("flash", self.start_ids["flash"])
        news_success, news_fail = self.crawl_category("news", self.start_ids["news"])

        if flash_success:
            new_flash_start = max(flash_success) + 1
            self.mongo_storage.update_one(
                {"_id": "theblockbeats"},
                {"flash_last_number": new_flash_start}
            )
            logger.info(f"[theblockbeats] 更新 flash_last_number 为 {new_flash_start}")
        else:
            logger.warning("[theblockbeats] flash栏目无文章成功爬取")

        if news_success:
            new_news_start = max(news_success) + 1
            self.mongo_storage.update_one(
                {"_id": "theblockbeats"},
                {"news_last_number": new_news_start}
            )
            logger.info(f"[theblockbeats] 更新 news_last_number 为 {new_news_start}")
        else:
            logger.warning("[theblockbeats] news栏目无文章成功爬取")

        return (f"[theblockbeats] 爬取结束: flash 成功 {len(flash_success)}，失败 {len(flash_fail)}; "
                f"news 成功 {len(news_success)}，失败 {len(news_fail)}")
