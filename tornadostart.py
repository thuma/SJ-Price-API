# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
import hlt
import snalltaget
import sj

application = tornado.web.Application([
    (r"/sj/", sj.SjHandler),
    (r"/hlt/", hlt.HltHandler),
    (r"/snalltaget/", snalltaget.SnalltagetHandler),
    (r"/sj/cache/", sj.CachePrint),
])

application.listen(8800)
tornado.ioloop.IOLoop.instance().start()
 