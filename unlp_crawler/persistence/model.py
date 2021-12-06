from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.types import TIMESTAMP
from datetime import datetime

Base = declarative_base()

class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ip = Column(String)
    certificate_hash = Column(String)
    pages = relationship('Page', backref='domain', lazy='dynamic')

class Page(Base):
    __tablename__ = 'page'

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('domain.id'))
    created_time   = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    url = Column(String)
    text = Column(String)
    title = Column(String)
    status = Column(String)
    body_hash = Column(String)
    scheme = Column(String)
    netloc = Column(String)
    hostname = Column(String)
    path = Column(String)
    port = Column(String)
    params = Column(String)
    query = Column(String)
    fragment = Column(String)
    filename = Column(String)
    javascripts = relationship('Javascript', backref='page', lazy='dynamic')
    csss = relationship('Css', backref='page', lazy='dynamic')
    forms = relationship('Form', backref='page', lazy='dynamic')
    links = relationship('Link', backref='page', lazy='dynamic')
    headers = relationship('Header', backref='page', lazy='dynamic')
    certificates = relationship('Certificate', backref='page', lazy='dynamic')
    comments = relationship('Comment', backref='page', lazy='dynamic')


class Javascript(Base):
    __tablename__ = 'javascript'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    js_type = Column(String)
    src = Column(String)
    md5 = Column(String)

class Css(Base):
    __tablename__ = 'css'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    rel = Column(String)
    href = Column(String)
    md5 = Column(String)

class Form(Base):
    __tablename__ = 'form'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    action = Column(String)
    method = Column(String)


class Header(Base):
    __tablename__ = 'header'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    name = Column(String)
    value = Column(String)

class Link(Base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    url = Column(String)

class Certificate(Base):
    __tablename__ = 'certificate'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    issuer = Column(String)
    pubkey = Column(String)
    certificate_hash = Column(String)

class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    comment = Column(String)
