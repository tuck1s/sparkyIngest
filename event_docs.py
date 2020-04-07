#!/usr/bin/env python3
#
from __future__ import print_function
import requests, json

out = '"{}","{}","{}","{}","{}","{}"'
docs = requests.get('https://api.sparkpost.com/api/v1/ingest/events/documentation')
res = docs.json()
print(out.format('type', 'attribute', 'required', 'reporting', 'sampleValue', 'description'))
for ev in res.get('results'):
    # Firstly, show the event type
    ev_name = ev.get('type').get('sampleValue')
    # Now iterate over the other field names
    for attrName, v  in ev.items():
        v_req = True if v.get('required') else False
        v_rep = True if v.get('reporting') else False
        v_sv = v.get('sampleValue')
        v_desc = v.get('description')
        print(out.format(ev_name, attrName, v_req, v_rep, v_sv, v_desc))