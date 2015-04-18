# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def store(operator, request, data):
	req = (request.getdate+request.getfrom+request.gettime+request.getto+request.gettotime).replace(':',"").replace('-',"")
	path = 'cache/%s/%s' % (operator, req)
	with open(path, 'w') as f:
		json.dump(data, f)


def get(operator, request):
	req = (request.getdate+request.getfrom+request.gettime+request.getto+request.gettotime).replace(':',"").replace('-',"")
	path = 'cache/%s/%s' % (operator, req)
	jfile = open(path, 'r')
	return json.load(jfile)