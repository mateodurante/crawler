import pymongo
from elasticsearch import Elasticsearch as ES
import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
from .model import Base, Domain, Page, Javascript, Css, Form, Header, Link, Certificate, Comment

class Persistence:
    def save(self, item):
        raise NotImplementedError

    def open(self):
        pass

    def close(self):
        pass

class ElasticSearchPersistence(Persistence):
    es_logger = logging.getLogger('elasticsearch')
    es_logger.setLevel(logging.WARNING)
    ELASTICSEARCH_INDEX_PAGES = 'pages'
    ELASTICSEARCH_INDEX_CERTS = 'certificates'
    ELASTICSEARCH_TYPE_PAGES = 'page'
    ELASTICSEARCH_TYPE_CERTS = 'certificate'

    def __init__(self, settings):
        self.settings = settings
        uri = "{}:{}".format(self.settings['ELASTICSEARCH_SERVER'], self.settings['ELASTICSEARCH_PORT'])
        self.es = ES([uri])
    
    def save(self, item):
        page = item['page']
        cert = item['certificate']
        self.es.index(index=f'{self.settings["ELASTICSEARCH_INDEX_PREFIX"]}-pages',
            doc_type=self.ELASTICSEARCH_TYPE_PAGES,
            id = item['id'],
            body = dict(page))
        if cert:
            self.es.update(index=f'{self.settings["ELASTICSEARCH_INDEX_PREFIX"]}-certificates',
                doc_type=self.ELASTICSEARCH_TYPE_CERTS,
                id=cert['certificate_hash'],
                body={'doc': dict(cert), 'doc_as_upsert': True})
            # op_type='create')
        # raise DropItem('If you want to discard an item')
        return item

    def open(self):
        pass

    def close(self):
        pass


class MongoDBPersistence(Persistence):
    COLLECTION_PAGE = 'unlp_page'
    COLLECTION_CERT = 'unlp_cert'

    def __init__(self, settings):
        self.settings = settings
        self.mongo_uri = "mongodb://{}:{}".format(self.settings['MONGO_SERVER'], self.settings['MONGO_PORT'])
        self.mongo_db = self.settings['MONGO_DATABASE']

    def open(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close(self):
        self.client.close()

    def save(self, item):
        page = item['page']
        page['page_id'] = item['id']
        cert = item['certificate']
        self.db[self.COLLECTION_PAGE].insert_one(dict(page))
        if cert:
            self.db[self.COLLECTION_CERT].replace_one({'certificate_hash': cert['certificate_hash']}, dict(cert), upsert=True)
        return item


class SQLAlchemyPersistence(Persistence):

    def __init__(self, settings):
        self.settings = settings
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def open(self):
        self.session = self.Session()

    def close(self):
        self.session.close()

    def save(self, item):
        ipage = item['page']
        cert = item['certificate']
        # convertir item en objetos de la base de datos
        domain = Domain(name=ipage['netloc'],ip=ipage['ip'],certificate_hash=ipage['certificate_hash'])
        page = Page(domain=domain,
            url=ipage['url'],
            text=ipage['text'],
            title=ipage['title'],
            status=ipage['status'],
            body_hash=ipage['body_hash'],
            scheme=ipage['scheme'],
            netloc=ipage['netloc'],
            hostname=ipage['hostname'],
            path=ipage['path'],
            port=ipage['port'],
            params=ipage['params'],
            query=ipage['query'],
            fragment=ipage['fragment'],
            filename=ipage['filename'])
        for js in ipage['js']:
            page.javascripts.append(Javascript(js_type=js['type'],src=js['src'],md5=js['md5']))
        for css in ipage['css']:
            page.csss.append(Css(rel=css['rel'],href=css['href'],md5=css['md5']))
        for f in ipage['forms']:
            try:
                page.forms.append(Form(action=f['action'],method=f['method']))
            except:
                pass
        for hn, hv in ipage['headers'].items():
            page.headers.append(Header(name=hn,value=hv))
        for l in ipage['links']:
            page.links.append(Link(url=l))
        for c in ipage['comments']:
            page.comments.append(Comment(comment=c))

        if cert:
            page.certificate = Certificate(certificate_hash=cert['certificate_hash'],
                issuer=cert['issuer'],
                pubkey=cert['pubkey'])

        domain.page = page

        self.session.add(domain)
        self.session.commit()

class SQLitePersistence(SQLAlchemyPersistence):
    def __init__(self, settings):
        self.engine = create_engine("sqlite:///{}".format(settings['SQLITE_DB']))
        super().__init__(settings)

class MySQLPersistence(SQLAlchemyPersistence):
    def __init__(self, settings):
        self.engine = create_engine("mysql+pymysql://{}:{}@{}/{}".format(settings['MYSQL_USER'],settings['MYSQL_PASSWORD'],settings['MYSQL_SERVER'],settings['MYSQL_DATABASE']))
        super().__init__(settings)

class PostgresPersistence(SQLAlchemyPersistence):
    def __init__(self, settings):
        self.engine = create_engine("postgres+psycopg2://{}:{}@{}/{}".format(settings['POSTGRES_USER'],settings['POSTGRES_PASSWORD'],settings['POSTGRES_SERVER'],settings['POSTGRES_DATABASE']))
        super().__init__(settings)
