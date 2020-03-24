#!/usr/bin/env python
#
from __future__ import print_function
import requests, gzip, json, time, uuid, os
from datetime import datetime

# Returns SparkPost formatted unique event_id, which needs to be a decimal string 0 .. (2^63-1).
# Python ints are arbitrary precision so we don't need to worry about arithmetic overflow
def uniq_event_id():
    u = uuid.uuid4().int  & 0x7fffffffffffffff # uuid4 gives us 128-bit random number, need to cut down to size
    return str(u)

# Returns a SparkPost formatted unique messageID, which has an embedded timestamp
def uniq_message_id():
    uID = uuid.uuid4().bytes
    tHex = '%08x' % (int(time.time()))
    tHexLittleEndian = tHex[6:8] + tHex[4:6] + tHex[2:4] + tHex[0:2] # reverse byte order
    u = '0000%s%02x%02x%02x%02x' % (tHexLittleEndian, uID[0], uID[1], uID[2], uID[3])
    return u

def uniq_recip_localpart():
    u = 'fred.bloggs.' + str(uuid.uuid4().int)[:12]
    return u


def make_open_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip):
    timestamp = int(time.time())
    e = {
        'msys': {
            'track_event': {
                'type': 'open',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'timestamp': str(timestamp),
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'subaccount_id': 0,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


def make_initial_open_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip):
    timestamp = int(time.time())
    e = {
        'msys': {
            'track_event': {
                'type': 'initial_open',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'timestamp': str(timestamp),
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'subaccount_id': 0,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


def make_click_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip):
    timestamp = int(time.time())
    e = {
        'msys': {
            'track_event': {
                'type': 'click',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'timestamp': str(timestamp),
                'target_link_url': 'https://example.com',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'subaccount_id': 0,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


def make_delivery_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip):
    timestamp = int(time.time())
    e = {
        'msys': {
            'message_event': {
                'type': 'delivery',
                'binding': 'mta1',
                'binding_group': 'hot chili',
                'campaign_id': campaign_id,
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'friendly_name': '',
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'msg_size': '315',
                'num_retries': '0',
                'open_tracking': True,                       # it's important that open_tracking is enabled if you want Signals Health Score to work
                'rcpt_to': rcpt_to,
                'recv_method': 'smtp',
                'routing_domain': rcpt_to.split('@')[1],
                'sending_ip': sending_ip,
                # 'rcpt_meta': {'pets' : 'dog'}, # You can include this, PowerMTA does not
                'subject': subject,
                'timestamp': str(timestamp),
                'subaccount_id': 0,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# The injection event is internally of type "reception"
def make_injection_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip):
    timestamp = int(time.time())
    e = {
        'msys': {
            'message_event': {
                'type': 'reception',
                'binding': 'mta1',
                'binding_group': 'hot chili',
                'campaign_id': campaign_id,
                # custom_message_id?? PowerMTA includes this, different to message_id
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'friendly_name': '',
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'msg_size': '315',
                'open_tracking': True,                       # it's important that open_tracking is enabled if you want Signals Health Score to work
                'rcpt_to': rcpt_to,
                'recv_method': 'smtp',
                'routing_domain': rcpt_to.split('@')[1],
                'sending_ip': sending_ip,
                # 'rcpt_meta': {'pets' : 'dog'}, # You can include this, PowerMTA does not
                'subject': subject,
                'timestamp': str(timestamp),
                'subaccount_id': 0,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'

# Note the bounce event type is "inband" not "bounce"
def make_bounce_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip):
    timestamp = int(time.time())
    e = {
        'msys': {
            'message_event': {
                'type': 'inband',
                'binding': 'mta1',
                'binding_group': 'hot chili',
                'bounce_class': '51',
                'campaign_id': campaign_id,
                # custom_message_id?? PowerMTA includes this, different to message_id
                'error_code': '550',
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'friendly_name': '',
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'msg_size': '',
                'num_retries': '0',
                'open_tracking': True,                       # it's important that open_tracking is enabled if you want Signals Health Score to work
                'raw_reason': 'smtp;550 5.7.1 spam 42',
                'recv_method': 'smtp',
                'routing_domain': rcpt_to.split('@')[1],
                'sending_ip': sending_ip,
                # 'rcpt_meta': {'pets' : 'dog'}, # You can include this, PowerMTA does not
                'subject': subject,
                'timestamp': str(timestamp),
                'subaccount_id': 0,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
if __name__ == "__main__":
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

    msg_from = 'test@bounces.test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
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
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, 1):
        # "successful" message sequence
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)
        time.sleep(2)
        events += make_delivery_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)
        time.sleep(2)
        events += make_initial_open_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)
        time.sleep(2)
        events += make_open_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)
        time.sleep(2)
        events += make_click_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)

        # "bounce" message sequence
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)
        time.sleep(2)
        events += make_bounce_event(msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, geo_ip, sending_ip)

    compressed_events = gzip.compress(events.encode('utf-8'))
    print('Uploading {} bytes of gzip event data'.format(len(compressed_events)))
    res = requests.post(url, data=compressed_events, headers=hdrs)
    print(res.status_code, res.content)