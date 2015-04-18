# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
print 'Loading id lists...'
#import hlt
#import jlt
#import klt
#import ltk
#import btr
#import dtr
#import xtr
#import mas
#import snalltaget
import sj
#import swebus
#import ot
import os

settings = {
    "static_path": os.getcwd()+"/static"
}

application = tornado.web.Application([
    (r"/sj/", sj.Handler),
    #(r"/sj/cache/", sj.CachePrint),
    #(r"/hlt/", hlt.Handler),
    #(r"/hlt/cache/", hlt.CachePrint),
    #(r"/klt/", klt.Handler),
    #(r"/klt/cache/", klt.CachePrint),
    #(r"/jlt/", jlt.Handler),
    #(r"/jlt/cache/", jlt.CachePrint),
    #(r"/ltk/", ltk.Handler),
    #(r"/ltk/cache/", ltk.CachePrint),
    #(r"/btr/", btr.Handler),
    #(r"/btr/cache/", btr.CachePrint),
    #(r"/dtr/", dtr.Handler),
    #(r"/dtr/cache/", dtr.CachePrint),
    #(r"/mas/", mas.Handler),
    #(r"/mas/cache/", mas.CachePrint),
    #(r"/xtr/", xtr.Handler),
    #(r"/xtr/cache/", xtr.CachePrint),
    #(r"/swebus/", swebus.Handler),
    #(r"/swebus/cache/", swebus.CachePrint),  
    #(r"/snalltaget/", snalltaget.Handler),
    #(r"/snalltaget/cache/", snalltaget.CachePrint),
    #(r"/ot/", ot.Handler),
    #(r"/ot/cache/", ot.CachePrint),
    #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+'/static'})
], **settings)

print 'Server started...'
application.listen(8800)
tornado.ioloop.IOLoop.instance().start()
 
