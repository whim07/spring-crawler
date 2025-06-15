from pymongo import MongoClient
from config import MONGODB_CONFIG


class MongoStorage:
    def __init__(self, uri=MONGODB_CONFIG["MONGO_URI"], db_name=MONGODB_CONFIG["MONGO_DB"]):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    # 获取各个网站开始的配置信息
    def get_start_config(self, source_name):
        return self.db.article_number.find_one({"_id": source_name})

    # TODO
    def update_one(self, filter_query, update_data, collection_name="article_number"):
        """更新指定集合中的单条记录"""
        self.db[collection_name].update_one(filter_query, {"$set": update_data})

    def insert(self, collection_name, data):
        collection = self.db[collection_name]
        if isinstance(data, list):
            result = collection.insert_many(data)
            return result.inserted_ids
        else:
            result = collection.insert_one(data)
            return result.inserted_id

    def find(self, collection_name, query=None):
        if query is None:
            query = {}
        collection = self.db[collection_name]
        return list(collection.find(query))

    def clear(self, collection_name):
        self.db[collection_name].delete_many({})
