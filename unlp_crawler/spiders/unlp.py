import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import Request
import scrapy
from w3lib.url import url_query_cleaner
import hashlib
import requests
from urllib import parse
import os
import time
from bs4 import BeautifulSoup

# import logging
# import sys
# from python_elastic_logstash import ElasticHandler, ElasticFormatter



# """
# Provide logger name simple without any special character
# Logger name will become as Elastic Search Index
# """
# root_logger = logging.getLogger(scrapy.core.downloader.tls)
# root_logger.setLevel(logging.DEBUG)

# elasticsearch_endpoint = 'http://localhost:9200' # No trailing slash

# elastic_handler = ElasticHandler(elasticsearch_endpoint, 'dev')  # Second argument is optional
# elastic_handler.setFormatter(ElasticFormatter())

# root_logger.addHandler(elastic_handler)

# # Extra is optional.
# extra = {
#     'elastic_fields': {
#         'version': 'python version: ' + repr(sys.version_info)
#     }
# }

# root_logger.debug("Python elastic logstash configured", extra=extra)


def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link

class UNLPCrawler(CrawlSpider):
    js_resources = {}
    css_resources = {}
    name = 'unlp'
    allowed_domains = ['unlp.edu.ar']
    # start_urls = ['https://unlp.edu.ar/']
    with open('domains', 'r') as f:
        domains = f.read().split('\n')
    start_urls = ['https://' + d for d in domains]
    start_urls += ['http://' + d for d in domains]
    rules = (
        Rule(
            LinkExtractor(
                deny=[
                    # re.escape('https://unlp.edu.ar/offsite'),
                    # re.escape('https://www.imdb.com/whitelist-offsite'),
                ],
            ),
            process_links=process_links,
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        u = parse.urlparse(response.url)
        f = os.path.basename(u.path)
        h = {k.decode(): v[0].decode() for k, v in response.headers.items()}

        extractor = LinkExtractor()
        links = [l.url for l in extractor.extract_links(response)]
        hostname_links = list(set([parse.urlparse(l.url).hostname for l in extractor.extract_links(response)]))

        sel = Selector(response)
        css = self.extract_css(response.url, sel)
        js = self.extract_js(response.url, sel)
        form = self.extract_form(response.url, sel)
        comments = sel.xpath('//comment()').extract()
        comments = list(set([c.replace('<!--', '').replace('-->', '').strip() for c in comments]))
        ts = int(time.time())
        if response.certificate:
            cert_hash = response.certificate.digest().decode().replace(':','').lower()
            certificate = {
                'timestamp': ts,
                'hostname': u.hostname,
                'port': u.port,
                'pubkey': str(response.certificate.dumpPEM()),
                'issuer': str(response.certificate.inspect()),
                'certificate_hash': cert_hash
                }
        else:
            cert_hash = ''
            certificate = {}
        
        item = { 
                'page': {
                    'timestamp': ts,
                    'url': response.url,
                    'text': response.text,
                    'title': response.xpath('//title/text()').get(),
                    'headers': h,
                    'status': response.status,
                    'body_hash': hashlib.md5(response.text.encode('utf-8')).hexdigest(),
                    'certificate_hash': cert_hash,
                    'ip': str(response.ip_address),
                    'js': js,
                    'css': css,
                    'scheme': u.scheme,
                    'netloc': u.netloc,
                    'hostname': u.hostname,
                    'port': u.port,
                    'path': u.path,
                    'params': u.params,
                    'query': u.query,
                    'fragment': u.fragment,
                    'filename': f,
                    'forms': form,
                    'comments': comments,
                    'links': links,
                    'hostname_links': hostname_links
                    },
                'certificate': certificate
            }

        return item
    
    def md5(self, data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()


    def extract_css(self, base_url, sel):
        css = sel.xpath('//link')
        items = []
        for c in css:
            href = (c.xpath('@href').extract() or [None])[0]
            rel = (c.xpath('@rel').extract() or [None])[0]
            if rel == 'stylesheet' and href:
                url = parse.urljoin(base_url, href)
                md5 = self.css_resources.get(url, '')
                if not md5:
                    x = requests.get(url=url).text
                    md5 = self.md5(x)
                    self.css_resources[url] = md5
                # else:
                #     print('css already in cache')
                items.append({'rel': rel, 'href': href, 'md5': md5})
        return items


    def extract_js(self, base_url, sel):
        js = sel.xpath('//script')
        items = []
        for j in js:
            src = (j.xpath('@src').extract() or [''])[0]
            jtype = (j.xpath('@type').extract() or [''])[0]
            url = ''
            md5 = ''
            if src:
                url = parse.urljoin(base_url, src)
                md5 = self.js_resources.get(url, '')
                if not md5:
                    u = parse.urlparse(url)
                    f = u.path.split('/')[-1]
                    if f.endswith('.js'):
                        x = requests.get(url=url).text
                        md5 = self.md5(x)
                        self.js_resources[url] = md5
                # else:
                #     print('js already in cache')
            else:
                md5 = self.md5(j.extract())
            data = {'type': jtype, 'src': src, 'md5': md5}
            items.append(data)
        return items


    def extract_form(self, base_url, sel):
        form = sel.xpath('//form')
        items = []
        for f in form:
            soup = BeautifulSoup(f.extract(), 'html.parser')
            attrs = soup.form.attrs
            attrs.pop('class', None)
            inputs = (f.xpath('input/@name').extract() or [''])[0]
            
            attrs['inputs'] = inputs
            items.append(attrs)
        return items

