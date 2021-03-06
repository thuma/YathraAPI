# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
print 'Loading id lists...'
import hlt
import jlt
import klt
import ltk
import btr
import dtr
import xtr
import mas
import svenskabuss
import snalltaget
import sj
import nettbuss
import bt
import sktr
import ot
import tib
import at
import vt
import nsb
import os

settings = {
    "static_path": os.getcwd()+"/static"
}

application = tornado.web.Application([
    (r"/bt/", bt.Handler),
    (r"/bt/cache/", bt.CachePrint),
    (r"/sj/", sj.Handler),
    #(r"/sj/cache/", sj.CachePrint),
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
    (r"/dtr/", dtr.Handler),
    (r"/dtr/cache/", dtr.CachePrint),
    (r"/mas/", mas.Handler),
    (r"/mas/cache/", mas.CachePrint),
    (r"/xtr/", xtr.Handler),
    (r"/xtr/cache/", xtr.CachePrint),
    (r"/snalltaget/", snalltaget.Handler),
    (r"/snalltaget/cache/", snalltaget.CachePrint),
    (r"/nettbuss/", nettbuss.Handler),
    (r"/nettbuss/cache/", nettbuss.CachePrint),
    (r"/sktr/", sktr.Handler),
    (r"/sktr/cache/", sktr.CachePrint),
    (r"/ot/", ot.Handler),
    #(r"/ot/cache/", ot.CachePrint),
    (r"/tib/", tib.Handler),
    (r"/tib/cache/", tib.CachePrint),
    (r"/at/", at.Handler),
    (r"/at/cache/", at.CachePrint),
    (r"/vt/", vt.Handler),
    (r"/vt/cache/", vt.CachePrint),
    (r"/nsb/", nsb.Handler),
    (r"/nsb/cache/", nsb.CachePrint),
    #(r"/sl/", sl.Handler),
    #(r"/sl/cache/", sl.CachePrint),
    (r"/svenskabuss/", svenskabuss.Handler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+'/static'})
], **settings)

print 'Server started...'
application.listen(8800)
tornado.ioloop.IOLoop.instance().start()
 
