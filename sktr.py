# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import xmltodict
import tornado.escape
import json
import time

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/skanerafiken-gtfs.csv')
    list_data = response.body
except httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
cache = {}
stops = {}
list_data = list_data.split('\n')

for row in list_data:
	try:
		parts = row.split(';')
		stops[parts[4]] = {}
		stops[parts[4]]['id'] = parts[3]
		stops[parts[4]]['name'] = parts[0]
	except:
		parts = ''

class CachePrint(tornado.web.RequestHandler):
	def get(self):
		global cache
		self.write(cache)

class Handler(tornado.web.RequestHandler):

	@tornado.web.asynchronous
	def get(self):
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		global cache
		global stops
		
		try:
			fromid = tornado.escape.url_escape(stops[self.get_argument('from')]['name'])+'|'+stops[self.get_argument('from')]['id']+'|0'
			toid = tornado.escape.url_escape(stops[self.get_argument('to')]['name'])+'|'+stops[self.get_argument('to')]['id']+'|0'
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
		try:
			deptime = time.strptime(self.get_argument('date')+self.get_argument('departureTime'),'%Y-%m-%d%H:%M')
			deptime = time.mktime(deptime)
			deptime = deptime-120
			deptime = time.gmtime(deptime)
			
		except:
			self.write({'error':'departureTime HH:MM missing / error, date YYYY-MM-DD missing / error'})
			self.finish()
			return
			
		try:
			date = time.strftime('%Y-%m-%d+%H:%M',deptime)
		except:
			self.write({'error':'date YYYY-MM-DD HH:MM missing / error'})
			self.finish()
			return

		searchurl = 'http://www.labs.skanetrafiken.se/v2.2/resultspage.asp?cmdaction=next&selPointFr='+fromid+'&selPointTo='+toid+'&LastStart='+date+'&NoOf=3&transportMode=31'

		self.myhttprequest = tornado.httpclient.HTTPRequest(searchurl, method='GET')
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		http_client = tornado.httpclient.HTTPClient()
		alldata = xmltodict.parse(response.body)
		alldata = alldata['soap:Envelope']['soap:Body']

		self.write(alldata)
		self.finish()
		return
