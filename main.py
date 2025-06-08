import concurrent.futures
import time

import schedule

import config
from db.mongo_storage import MongoStorage
from crawler.spider_zhinitaimei import ZhiNiTaiMeiCrawler
from crawler.spider_2jmtt import JMTTCrawler
from crawler.spider_cryptotradingcafe import CryptoTradingCafeCrawler
from crawler.spyder_theblockbeats import TheBlockBeatsCrawler
from data_etl.spider_to_dwi import SourceToDwi


def run_crawler(crawler):
    return crawler.crawl()


def main():
    user_agents = config.USER_AGENTS
    mongo_storage = MongoStorage()

    crawlers = [
        CryptoTradingCafeCrawler(user_agents, mongo_storage=mongo_storage),
        ZhiNiTaiMeiCrawler(user_agents, mongo_storage=mongo_storage),
        JMTTCrawler(user_agents, mongo_storage=mongo_storage),
        TheBlockBeatsCrawler(user_agents, mongo_storage=mongo_storage)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(crawlers)) as executor:
        futures = [executor.submit(run_crawler, crawler) for crawler in crawlers]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print("爬虫执行结果:", result)
            except Exception as e:
                print("爬虫执行异常:", e)
    data_trans = SourceToDwi(mongo_storage, config.BATCH_ID)
    data_trans.data_trans()

    # data_trans = SourceToDwi(mongo_storage, "20250603232849")
    # data_trans.data_trans()


if __name__ == "__main__":
    schedule.every().day.at("18:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次任务
