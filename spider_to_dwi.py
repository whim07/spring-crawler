import re
import time
from collections import defaultdict
from datetime import datetime

import config
from utils.logger import get_logger

logger = get_logger(__name__, log_file="logs/source_to_dwi.log")


class SourceToDwi:
    def __init__(self, mongo_storage, batch_id):
        self.mongo_storage = mongo_storage
        self.batch_id = batch_id
        self.db = self.mongo_storage.db
        self.BATCH_SIZE = config.BATCH_SIZE
        self.ids = defaultdict(int)
        logger.info(f"[SourceToDwi] batchId={self.batch_id}, DB={self.db.name}")

    def parse_to_timestamp(self, timestr):
        timestr = timestr.strip()

        # 类型 1：2023年03月23日 21:58发布
        if re.match(r"\d{4}年\d{1,2}月\d{1,2}日 \d{1,2}:\d{2}发布", timestr):
            try:
                dt = datetime.strptime(timestr.replace("发布", ""), "%Y年%m月%d日 %H:%M")
                return int(dt.timestamp())
            except Exception as e:
                logger.warning(f"[WARN] 时间格式转换失败(type1): {timestr}, 错误: {e}")
                return -1

        # 类型 2：2025-05-29 11:48
        try:
            dt = datetime.strptime(timestr, "%Y-%m-%d %H:%M")
            return int(dt.timestamp())
        except ValueError:
            pass

        # 类型 3：2025-05-27
        try:
            dt = datetime.strptime(timestr, "%Y-%m-%d")
            return int(dt.timestamp())
        except ValueError:
            pass

        # 类型 4：2025 5 21
        try:
            dt = datetime.strptime(timestr, "%Y %m %d")
            return int(dt.timestamp())
        except ValueError:
            pass

        logger.warning(f"[WARN] 未知时间格式: {timestr}")
        return -1

    def create_id(self, create_time):
        ts = self.parse_to_timestamp(create_time)
        if ts < 0:
            logger.warning(f"[WARN] 无效的创建时间: {create_time}，使用当前时间戳代替。")
            ts = int(time.time())
        new_id = ts * 1000 + self.ids[ts]
        self.ids[ts] += 1
        return new_id

    def data_trans(self):
        source_collections = [
            "source_data_theblockbeats",
            "source_data_cryptotradingcafe",
            "source_data_jmtt",
            "source_data_zhinitaimei"
        ]
        target_collection = self.db["dwi_spider_data"]
        query_filter = {"batchId": self.batch_id}

        for i, collection_name in enumerate(source_collections):
            source = self.db[collection_name]
            count = source.count_documents(query_filter)
            logger.info(f"[INFO] 处理集合: {collection_name}，符合 batchId={self.batch_id} 的数据条数: {count}")
            if count == 0:
                logger.warning(f"[WARN] 集合 {collection_name} 中没有匹配的数据，跳过")
                continue

            cursor = source.find(query_filter, no_cursor_timeout=True).batch_size(self.BATCH_SIZE)
            batch = []
            try:
                for doc in cursor:
                    new_doc = {
                        "_source": collection_name,
                        "source_type": i + 1,
                        "article_title": doc.get("title", ""),
                        "article_desc": doc.get("content", ""),
                        "source_write_time": doc.get("create_time", ""),
                        "source_link": doc.get("url", ""),
                        "batchId": doc.get("batchId", ""),
                    }
                    new_doc["_id"] = self.create_id(doc.get("create_time", ""))
                    new_doc["write_time"] = self.parse_to_timestamp(doc.get("create_time", "")) * 1000

                    batch.append(new_doc)

                    if len(batch) >= self.BATCH_SIZE:
                        target_collection.insert_many(batch)
                        logger.info(f"[INFO] 写入批次 {len(batch)} 条数据到目标集合 dwi_spider_data")
                        batch.clear()

                if batch:
                    target_collection.insert_many(batch)
                    logger.info(f"[INFO] 写入剩余 {len(batch)} 条数据到目标集合 dwi_spider_data")
            except Exception as e:
                logger.error(f"[ERROR] 处理集合 {collection_name} 时发生异常: {e}")
            finally:
                cursor.close()

        logger.info(f"[SUCCESS] 所有集合中 batchId={self.batch_id} 的数据已合并完毕。")
