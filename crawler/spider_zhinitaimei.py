import random
import re
import requests
from bs4 import BeautifulSoup
import config
from .base import BaseCrawler
from utils.logger import get_logger

logger = get_logger("zhinitaimei", log_file="logs/zhinitaimei.log")


class ZhiNiTaiMeiCrawler(BaseCrawler):
    def __init__(self, user_agents, mongo_storage):
        super().__init__(user_agents)
        self.mongo_storage = mongo_storage
        self.batch_id = config.BATCH_ID
        self.start_id = self.get_start_id()

    def get_start_id(self):
        config_entry = self.mongo_storage.get_start_config("zhinitaimei")
        if config_entry and "last_number" in config_entry:
            return int(config_entry["last_number"])
        return 1

    def get_article(self, article_id):
        url = f"https://www.zhinitaimei.com/{article_id}/"
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Referer": "https://www.zhinitaimei.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            # 抓取元素
            title_el = soup.select_one("h1.article-title a")
            author_el = soup.select_one(".article-avatar .display-name")
            create_time_el = soup.select_one(".muted-2-color span")
            content_el = soup.select_one(".article-content")

            if not all([title_el, author_el, create_time_el, content_el]):
                return None

            # 清洗内容
            content_text = re.sub(r'© 版权声明.*$', "", content_el.get_text(strip=False), flags=re.DOTALL)

            return {
                "url": url,
                "title": title_el.get_text(strip=True),
                "content": content_text.strip(),
                "create_time": create_time_el.get("title"),
                "author": author_el.get_text(strip=True),
                "batchId": self.batch_id,
                "jobId": article_id
            }
        except Exception as e:
            logger.exception(f"Error fetching {url}: {e}")
            return None

    def crawl(self):
        current_id = self.start_id
        success_ids = []
        fail_ids = []

        logger.info(f"[zhinitaimei] Start crawling from article ID {current_id}")

        # 第一阶段：尝试抓取直到失败文章达到 50 个
        while len(fail_ids) < config.MAX_WAIT_ARTICLES:
            try:
                article = self.get_article(current_id)
                if article:
                    self.mongo_storage.insert("source_data_zhinitaimei", article)
                    success_ids.append(current_id)
                else:
                    logger.warning(f"[zhinitaimei] Article ID {current_id} fetch failed or incomplete.")
                    fail_ids.append(current_id)
            except Exception as e:
                logger.error(f"[zhinitaimei] Exception occurred while fetching article ID {current_id}: {e}",
                             exc_info=True)
                fail_ids.append(current_id)
            current_id += 1

        logger.info(f"[zhinitaimei] Enter retry stage with {len(fail_ids)} failed IDs")

        # 第二阶段：对失败的文章重试三次
        retried_success_ids = []
        for i in range(config.MAX_RETRIES):
            still_failed = []
            for fid in fail_ids:
                try:
                    article = self.get_article(fid)
                    if article:
                        self.mongo_storage.insert("source_data_zhinitaimei", article)
                        retried_success_ids.append(fid)
                    else:
                        logger.warning(f"[zhinitaimei] Retry {i + 1}: Article ID {fid} fetch failed.")
                        still_failed.append(fid)
                except Exception as e:
                    logger.error(f"[zhinitaimei] Retry {i + 1}: Exception while fetching article ID {fid}: {e}",
                                 exc_info=True)
                    still_failed.append(fid)
            fail_ids = still_failed
            if not fail_ids:
                break

        # 更新 article_number 中的起始编号
        all_success = success_ids + retried_success_ids
        if all_success:
            max_id = max(all_success) + 1
            try:
                self.mongo_storage.update_one(
                    {"_id": "zhinitaimei"},
                    {"last_number": max_id}
                )
                logger.info(f"[zhinitaimei] Updated last_number to {max_id}")
            except Exception as e:
                logger.error(f"[zhinitaimei] Failed to update last_number in DB: {e}", exc_info=True)
        else:
            logger.warning("[zhinitaimei] No articles successfully fetched.")

        return f"[zhinitaimei] Done. Success: {len(all_success)}, Failed: {len(fail_ids)}"
