# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy.utils.project import get_project_settings
from elasticsearch import Elasticsearch as ES
import uuid
import logging
from .persistence.types import ElasticSearchPersistence, MongoDBPersistence, SQLitePersistence

# class UnlpCrawlerPipeline:
#     def process_item(self, item, spider):
#         return item

class PreparePipeline:
    def process_item(self, item, spider):
        item['id'] = str(uuid.uuid4())
        return item

# class CertificatePipeline:
#     def process_item(self, item, spider):
#         item['_index'] = 'certificates'
#         item['_type'] = 'certificates'

#         item['page_id'] = item['_id']
        
#         return item

class PersistencePipeline:

    def __init__(self):
        self.settings = get_project_settings()
        self.persistence_items = {
            'elasticsearch': ElasticSearchPersistence,
            'mongodb': MongoDBPersistence,
            'sqlite': SQLitePersistence
        }
        self.persistence_type = self.settings['PERSISTENCE_TYPE']
        self.persistence = self.persistence_items[self.persistence_type](self.settings)

    def process_item(self, item, spider):
        self.persistence.save(item)

    def open_spider(self, spider):
        self.persistence.open()

    def close_spider(self, spider):
        self.persistence.close()


# class ElasticSearchPipeline:
#     es_logger = logging.getLogger('elasticsearch')
#     es_logger.setLevel(logging.WARNING)

#     def __init__(self):
#         self.settings = get_project_settings()
#         uri = "{}:{}".format(self.settings['ELASTICSEARCH_SERVER'], self.settings['ELASTICSEARCH_PORT'])
#         self.es = ES([uri])
    
#     def process_item(self, item, spider):
#         page = item['page']
#         cert = item['certificate']
#         self.es.index(index=self.settings['ELASTICSEARCH_INDEX_PAGES'],
#             doc_type=self.settings['ELASTICSEARCH_TYPE'],
#             id = item['id'],
#             body = dict(page))
#         if cert:
#             self.es.update(index=self.settings['ELASTICSEARCH_INDEX_CERTS'],
#                 doc_type=self.settings['ELASTICSEARCH_TYPE_CERTS'],
#                 id=cert['certificate_hash'],
#                 body={'doc': dict(cert), 'doc_as_upsert': True})
#             # op_type='create')
#         # raise DropItem('If you want to discard an item')
#         return item



# class MongoDBPipeline:

#     collection_name_page = 'unlp_page'
#     collection_name_cert = 'unlp_cert'

#     def __init__(self):
#         self.settings = get_project_settings()
#         self.mongo_uri = "mongodb://{}:{}".format(self.settings['MONGO_SERVER'], self.settings['MONGO_PORT'])
#         self.mongo_db = self.settings['MONGO_DATABASE']

#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]

#     def close_spider(self, spider):
#         self.client.close()

#     def process_item(self, item, spider):
#         page = item['page']
#         page['page_id'] = item['id']
#         cert = item['certificate']
#         self.db[self.collection_name_page].insert_one(dict(page))
#         if cert:
#             self.db[self.collection_name_cert].replace_one({'certificate_hash': cert['certificate_hash']}, dict(cert), upsert=True)
#         return item
