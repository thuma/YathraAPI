# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
import hlt
import jlt
import klt
import ltk
import btr
import dtr
import xtr
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
    (r"/klt/", klt.Handler),
    (r"/klt/cache/", klt.CachePrint),
    (r"/jlt/", jlt.Handler),
    (r"/jlt/cache/", jlt.CachePrint),
    (r"/ltk/", ltk.Handler),
    (r"/ltk/cache/", ltk.CachePrint),
    (r"/btr/", btr.Handler),
    (r"/btr/cache/", btr.CachePrint),
    (r"/dtr/", btr.Handler),
    (r"/dtr/cache/", btr.CachePrint),
    (r"/xtr/", btr.Handler),
    (r"/xtr/cache/", btr.CachePrint),    
    (r"/snalltaget/", snalltaget.Handler),
    (r"/snalltaget/cache/", snalltaget.CachePrint),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+'/static'})
], **settings)

application.listen(8800)
tornado.ioloop.IOLoop.instance().start()
 
