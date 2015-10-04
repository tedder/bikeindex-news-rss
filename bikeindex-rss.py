#!/usr/bin/env python3

# (c) Ted Timmons, MIT license, contact me if you need more details.

import requests
from lxml import html
import lxml
import PyRSS2Gen
import boto3
import datetime
import io

LINK = 'https://bikeindex.org/news'
page = requests.get(LINK)
try:
  tree = html.fromstring(page.text)
except lxml.etree.XMLSyntaxError:
  if page.status_code == 500:
    sys.exit(0)
  print("page failed. %s" % page.status_code)

rssitems = []

items = tree.xpath('//ul[@class="news-index-list"]/li')
for item in items:
  link = item.xpath('normalize-space(h2/a/@href)')
  img = item.xpath('normalize-space(a[@class="index-image-link"]/img/@src)')
  title = item.xpath('normalize-space(h2/a/span/text())')
  txt = item.xpath('normalize-space(p[@class="blog-index"]/text())')
  #print(item, itemlink)
  print(link, img, title, txt)

  rssitems.append(PyRSS2Gen.RSSItem(
    title = title,
    link = link,
    guid = link,
    description = txt
    #pubDate = parsedDate # no date in html
  ))

rss = PyRSS2Gen.RSS2(
  title = 'Bikeindex News feed',
  link = LINK,
  ttl = 3600, # cache 6hrs
  docs = 'https://github.com/tedder/bikeindex-news-rss',
  description = 'news from stolen bike index',
  lastBuildDate = datetime.datetime.now(),
  items = rssitems
)

rssfile = io.StringIO()
rss.write_xml(rssfile)

s3 = boto3.resource('s3')
s3.Bucket('dyn.tedder.me').put_object(
  Key='rss/bikeindex-news.xml',
  Body=rssfile.getvalue(),
  ACL='public-read',
  CacheControl='public, max-age=3600',
  StorageClass='REDUCED_REDUNDANCY',
  ContentType='text/xml')
