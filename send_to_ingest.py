#!/usr/bin/env python
#
from __future__ import print_function
import requests, gzip, json, time, uuid, os
from datetime import datetime


def uniq_event_id():
    u = str(uuid.uuid4().int)[:17]
    return u

def uniq_message_id():
    u = '00000' + str(uuid.uuid4().hex)[:16]
    return u

def uniq_recip_localpart():
    u = 'fred.bloggs.' + str(uuid.uuid4().int)[:12]
    return u

def make_bounce_event(msg_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip):
    timestamp = time.time()
    td = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    e = {
        'msys': {
            'message_event': {
                'type': 'inband',
                'binding_group': 'hot chili',
                'binding': '10.0.0.1',
                'bounce_class': '10',
                'campaign_id': campaign_id,
                'click_tracking': '1',
                'delv_method': 'esmtp',                     # marked as 'required' in /documentation output
                'error_code': '551',
                'event_id': uniq_event_id(),
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'msg_size': '315',
                'num_retries': '0',
                'open_tracking': '1',
                'raw_reason': '551 5.7.0 User has gone away, so should you',
                'rcpt_tags': [],
                'recv_method': 'rest',
                'routing_domain': rcpt_to.split('@')[1],
                'rcpt_to': rcpt_to,
                'rcpt_meta': {'pets' : 'dog'},
                'reason': '551 5.7.0 [internal] recipient blackholed',
                'subject': subject,
                'timestamp': str(int(timestamp)),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


def make_open_event(msg_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip):
    timestamp = time.time()
    td = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    e = {
        'msys': {
            'track_event': {
                'type': 'open',
                'campaign_id': campaign_id,
                'click_tracking': '1',
                'delv_method': 'esmtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'initial_pixel': False,
                'message_id': uniq_msg_id,
                'rcpt_tags': [],
                'routing_domain': rcpt_to.split('@')[1],
                'rcpt_to': rcpt_to,
                'open_tracking': '1',
                'msg_from': msg_from,
                'rcpt_meta': {'pets' : 'dog'},
                'subject': subject,
                'timestamp': str(int(timestamp)),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


def make_click_event(msg_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip):
    timestamp = time.time()
    td = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    e = {
        'msys': {
            'track_event': {
                'type': 'click',
                'campaign_id': campaign_id,
                'click_tracking': '1',
                'delv_method': 'esmtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'initial_pixel': False,
                'message_id': uniq_msg_id,
                'rcpt_tags': [],
                'routing_domain': rcpt_to.split('@')[1],
                'rcpt_to': rcpt_to,
                'open_tracking': '1',
                'msg_from': msg_from,
                'rcpt_meta': {'pets' : 'dog'},
                'subject': subject,
                'timestamp': str(int(timestamp)),
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
    print('Environment variable SPARKPOST_API_KEY not set - stopping.')
    exit(1)

hdrs = {
    'Authorization': apiKey,
    'Content-Type': 'application/x-ndjson',
    'Content-Encoding': 'gzip'
}

msg_from = 'sp-event-agent@test.sparkpost.com'
campaign_id = 'big nice campaign'
subject = 'lovely test email'
geo_ip = {
    'country': 'US',
    'region': 'MD',
    'city': 'Columbia',
    'latitude': 39.1749,
    'longitude': -76.8375,
    'zip': 21046,
    'postal_code': '21046',
}

events = ''
for i in range(0, 1):
    rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
    uniq_msg_id = uniq_message_id()
    events += make_bounce_event(msg_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip)
    events += make_open_event(msg_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip)
    events += make_click_event(msg_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip)

compressed_events = gzip.compress(events.encode('utf-8'))
print('Uploading {} bytes of gzip event data'.format(len(compressed_events)))
res = requests.post(url, data=compressed_events, headers=hdrs)
print(res.status_code, res.content)