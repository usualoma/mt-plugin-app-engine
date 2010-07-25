#!/usr/bin/env python
#
# Copyright (c) 2010 ToI Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import urllib
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.ext.webapp import template
from django.template import Context, Template

import mimetypes

template_cache = {}
class MainHandler(webapp.RequestHandler):
	def get(self, url):
		template, type = template_cache.get(url, (None, None))
#		template, type = (None, None)

		if not template:
			page = Page.gql('WHERE url = :url', url=url).get() or Page.gql('WHERE url = :url', url=url+'index.html').get() or Page.gql('WHERE url = :url', url=url+'/index.html').get()

			if page:
				template = Template(page.content.encode('utf-8'))
				type, encoding = mimetypes.guess_type(page.url)

				template_cache[page.url] = (template, type)
			else:
				self.error(404)
				return self.response.out.write('Page Not Found')

		content = Context({})
		if type:
			self.response.headers["Content-Type"] = type

		self.response.out.write(template.render(content))

	def post(self, url):
		mt = MovableType.gql(
			'WHERE address = :address',
			address=self.request.remote_addr
		).get()
		if not mt:
			self.error(405)
			return self.response.out.write('Not Allowed')


		url = urllib.quote(self.request.get('url'))

		page = Page.gql('WHERE url = :url', url=url).get()
		if not page:
			page = Page(
				url = url
			)
		page.content = self.request.get('content')
		page.put()

		if url in template_cache:
			del template_cache[url]

		self.response.out.write('OK')


# ページ
class Page(db.Model):
	url	    = db.StringProperty()
	content = db.TextProperty()

# 更新元 (IPアドレスで制限)
class MovableType(db.Model):
	address = db.StringProperty()

if not MovableType.gql('WHERE address = :address', address='192.0.2.0').get():
	MovableType(address='192.0.2.0').put()


def main():
	application = webapp.WSGIApplication([
		('/(.*)', MainHandler),
	], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
