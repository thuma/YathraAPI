# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
import hlt
import jlt
import snalltaget
import sj
import os

settings = {
    "static_path": os.getcwd()+"/static"
}

application = tornado.web.Application([
    (r"/sj/", sj.Handler),
    (r"/sj/cache/", sj.CachePrint),
    (r"/hlt/", hlt.Handler),
    (r"/hlt/cache/", hlt.CachePrint),
    (r"/jlt/", jlt.Handler),
    (r"/jlt/cache/", jlt.CachePrint),
    (r"/snalltaget/", snalltaget.Handler),
    (r"/snalltaget/cache/", snalltaget.CachePrint),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+'/static'})
], **settings)

application.listen(8800)
tornado.ioloop.IOLoop.instance().start()
 
