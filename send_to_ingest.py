#!/usr/bin/env python
#
from __future__ import print_function
import requests, gzip, json, time, uuid, os
from datetime import datetime


def uniq_event_id():
    # '12345678358769062'
    return str(uuid.uuid4().int)[:17]


def uniq_message_id():
    u = '00000' + str(uuid.uuid4().hex)[:16]
    return u


def make_bounce_event(msg_from, rcpt_to):
    timestamp = time.time()
    td = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    e = {
        'msys': {
            'message_event': {
                'type': 'inband',
                'msg_size': '315',
                'bounce_class': '10',
                'rcpt_tags': [],
                'recv_method': 'rest',
                'binding_group': 'hot chili',
                'routing_domain': rcpt_to.split('@')[1],
                'binding': 'default',
                'rcpt_to': rcpt_to,
                'open_tracking': '1',
                'msg_from': msg_from,
                'raw_reason': '551 5.7.0 User has gone away, so should you',
                'rcpt_meta': {"pets" : "dog"},
                'error_code': '551',
                'message_id': uniq_message_id(),
                'reason': '551 5.7.0 [internal] recipient blackholed',
                'click_tracking': '1',
                'num_retries': '0',
                'event_id': uniq_event_id(),
                'subject': 'sp event agent checking in',
                'timestamp': str(int(timestamp)),
                'snippet_count': '0',
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
url = 'https://api.sparkpost.com/api/v1/ingest/events'
apiKey = os.getenv('SPARKPOST_API_KEY')
if apiKey == None:
    print('SPARKPOST_API_KEY not set - stopping.')
    exit(1)

hdrs = {
    'Authorization': apiKey,
    'Content-Type': 'application/x-ndjson',
    'Content-Encoding': 'gzip'
}

events = ''
for i in range(0, 1):
    events += make_bounce_event(msg_from='sp-event-agent@test.sparkpost.com', rcpt_to='test@ingest8.thetucks.com')
#    events += make_injection_event(batchname)

compressed_events = gzip.compress(events.encode('utf-8'))
print('Uploading {} bytes of gzip event data'.format(len(compressed_events)))
res = requests.post(url, data=compressed_events, headers=hdrs)
print(res.status_code, res.content)