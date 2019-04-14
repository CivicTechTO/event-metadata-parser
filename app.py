from flask import Flask, request, render_template, jsonify
from flaskext.markdown import Markdown
import json
import requests
import urllib
from scrapy.selector import Selector

app = Flask(__name__)
Markdown(app)

@app.route('/')
def help():
    return render_template('help.html')

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route('/<path:url>')
def process(url):
    # Reconstitute url querystrings that flask got greedy with
    querystrings = urllib.parse.urlencode(request.args)
    url = url + '?' + querystrings
    return jsonify(get_data(url))

def get_data(url):
    r = requests.get(url)
    sel = Selector(r)
    if sel.xpath('//meta[@property="og:type"]/@content').extract_first() == 'events.event':
        data = {
            'url': sel.xpath('//link[@rel="canonical"]/@href').extract_first(),
            'title': sel.xpath('//meta[@property="og:title"]/@content').extract_first(),
            'description': sel.xpath('//meta[@property="og:description"]/@content').extract_first().strip(),
            'start_time': sel.xpath('//meta[@property="event:start_time"]/@content').extract_first(),
            'end_time': sel.xpath('//meta[@property="event:end_time"]/@content').extract_first(),
            'location': sel.xpath('//meta[@name="twitter:data1"]/@value').extract_first(),
        }

        return data

    if sel.xpath('//meta[@property="og:type"]/@content').extract_first() == 'uniiverse:listing':
        data = {
            'url': sel.xpath('//link[@rel="canonical"]/@href').extract_first(),
            'title': sel.xpath('//meta[@property="og:title"]/@content').extract_first(),
            'description': sel.xpath('//*[@itemprop="description"]/text()').extract_first().strip(),
            'start_time': sel.xpath('//*[@itemprop="startDate"]/text()').extract_first(),
            'end_time': sel.xpath('//*[@itemprop="endDate"]/text()').extract_first(),
            'location': sel.xpath('//*[@itemprop="location"]/text()').extract_first(),
        }
        return data

    return {}

