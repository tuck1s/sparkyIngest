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


class FakeTimestamp:
    def __init__(self, begintime, naptime):
        self.ts = begintime
        self.naptime = naptime

    def time(self):
        self.ts += self.naptime                 # increment this so events appear spaced apart
        return self.ts


# Note the ingest event type is "reception", the SparkPost event type is "injection"
def make_injection_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip):
    timestamp = ts.time()
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
                'subaccount_id': 0,
                'subject': subject,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "delivery", the SparkPost event type is "delivery"
def make_delivery_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip):
    timestamp = ts.time()
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
                'subaccount_id': 0,
                'subject': subject,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "initial_open", the SparkPost event type is "initial_open"
def make_initial_open_event(ts, rcpt_to, uniq_msg_id, geo_ip):
    timestamp = ts.time()
    e = {
        'msys': {
            'track_event': {
                'type': 'initial_open',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "open", the SparkPost event type is "open"
def make_open_event(ts, rcpt_to, uniq_msg_id, geo_ip):
    timestamp = ts.time()
    e = {
        'msys': {
            'track_event': {
                'type': 'open',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "click", the SparkPost event type is "click"
def make_click_event(ts, rcpt_to, uniq_msg_id, geo_ip):
    timestamp = ts.time()
    e = {
        'msys': {
            'track_event': {
                'type': 'click',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'target_link_url': 'https://example.com',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "inband", the SparkPost event type is "bounce"
def make_bounce_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, bounce_code, bounce_reason, bounce_class, raw_reason):
    timestamp = ts.time()
    e = {
        'msys': {
            'message_event': {
                'type': 'inband',
                'binding': 'mta1',
                'binding_group': 'hot chili',
                'bounce_class': bounce_class,
                'campaign_id': campaign_id,
                # custom_message_id?? PowerMTA includes this, different to message_id
                'error_code': bounce_code,
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'friendly_name': '',
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'msg_size': '',
                'num_retries': '0',
                'open_tracking': True,                       # it's important that open_tracking is enabled if you want Signals Health Score to work
                'raw_reason': bounce_reason,
                'rcpt_to': rcpt_to,
                'reason': bounce_reason,
                'recv_method': 'smtp',
                'routing_domain': rcpt_to.split('@')[1],
                'sending_ip': sending_ip,
                'subject': subject,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'

# Note the ingest event type is "outofband", the SparkPost events type is "out_of_band"
def make_out_of_band_bounce_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, bounce_code, bounce_reason, bounce_class, raw_reason):
    timestamp = ts.time()
    e = {
        'msys': {
            'message_event': {
                'type': 'outofband',
                'bounce_class': bounce_class,
                # custom_message_id?? PowerMTA includes this, different to message_id
                'delv_method': 'smtp',
                'error_code': bounce_code,
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                # 'friendly_name': '',
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'raw_reason': raw_reason,
                'rcpt_to': rcpt_to,
                'reason': bounce_reason,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "feedback", the SparkPost event type is "spam_complaint"
def make_spam_complaint_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip):
    timestamp = ts.time()
    e = {
        'msys': {
            'message_event': {
                'type': 'feedback',
                # custom_message_id?? PowerMTA includes this, different to message_id
                'delv_method': 'smtp',
                'event_id': uniq_event_id(),
                'fbtype': 'abuse', # required
                'friendly_from': friendly_from,
                'message_id': uniq_msg_id,
                # 'msg_from': msg_from,                       # PowerMTA does not include this attribute - should it be?
                'rcpt_to': rcpt_to,
                'report_by': '',                              # Should this be populated?
                'sending_ip': sending_ip,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "tempfail", the SparkPost event type is "delay"
def make_delay_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, bounce_code, bounce_reason, bounce_class, raw_reason):
    timestamp = ts.time()
    e = {
        'msys': {
            'message_event': {
                'type': 'tempfail',
                'binding': 'mta1',
                'binding_group': 'hot chili',
                'bounce_class': bounce_class,
                'campaign_id': campaign_id,
                # custom_message_id?? PowerMTA includes this, different to message_id
                'error_code': bounce_code, # 452
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'friendly_name': '',
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'msg_size': '',
                'num_retries': '0',
                'open_tracking': True,                       # it's important that open_tracking is enabled if you want Signals Health Score to work
                'queue_time': "0",                           # try varying this?
                'raw_reason': bounce_reason,
                'rcpt_to': rcpt_to,
                'reason': bounce_reason,
                'recv_method': 'smtp',
                'routing_domain': rcpt_to.split('@')[1],
                'sending_ip': sending_ip,
                'subaccount_id': 0,
                'subject': subject,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'

#
# -----------------------------------------------------------------------------------------
# Return n repeats of a "successful" event sequence, with time between events
# -----------------------------------------------------------------------------------------
#
def make_success_events_sequence(ts, n):
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
    for i in range(0, n):
        # "successful" message sequence
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_delivery_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_initial_open_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip)
        events += make_open_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip)
        events += make_click_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip)
    return events

#
# Return n repeats of a "bounce" event sequence, with time between events
#
def make_bounce_events_sequence(ts, n):
    msg_from = 'test@bounces.test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'big bouncy campaign'
    subject = 'This email results in an in-band bounce'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        # "bounce" message sequence
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        bounce_code = '554'
        bounce_reason = 'smtp;554 5.7.1 Blacklisted by black.uribl.com Contact the postmaster of this domain for resolution.'
        raw_reason = bounce_reason # no need to redact this type of reason code
        bounce_class = '51'
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_bounce_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)
    return events


def make_out_of_band_bounce_events_sequence(ts, n):
    msg_from = 'test@oob-bounces.test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'out of band bouncy campaign'
    subject = 'out of band bounce test email'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        # "Out of band" bounce message sequence, should have a corresponding injection & delivery
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        bounce_code = '550'
        raw_reason = 'SMTP;550 5.0.0 <' + rcpt_to + '>... User unknown'
        bounce_reason = 'SMTP;550 5.0.0 ...@... ...' # redacted the email address for this type of reason code
        bounce_class = '10'
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_delivery_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_out_of_band_bounce_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)
    return events


def make_spam_complaint_events_sequence(ts, n):
    msg_from = 'test@test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'campaign that gets a spam complaint FBL'
    subject = 'message that gets spam complaint FBL'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        # "Out of band" bounce message sequence, should have a corresponding injection & delivery
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_delivery_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        events += make_spam_complaint_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
    return events


def make_delay_events_sequence(ts, n):
    msg_from = 'test@test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'campaign that gets delayed'
    subject = 'message that gets delayed'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        # "Out of band" bounce message sequence, should have a corresponding injection & delivery
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        bounce_code = '452'
        raw_reason = 'smtp;452 4.2.2 Recipient Unable to accept message - mailbox full(c2mailmx101)'
        bounce_reason = raw_reason # redacted the email address for this type of reason code
        bounce_class = '22' # Mailbox full
        events += make_delay_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)
    return events


def send_to_ingest(compressed_events):
    print('Uploading {} bytes of gzip event data'.format(len(compressed_events)))
    res = requests.post(url, data=compressed_events, headers=hdrs)
    print(res.status_code, res.content)


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

    # "wind the clock back", to allow for events spread apart in time
    ts = FakeTimestamp(int(time.time()) - 10*60, 2)

    events = make_success_events_sequence(ts, 1)
    events += make_bounce_events_sequence(ts, 1)
    send_to_ingest(gzip.compress(events.encode('utf-8')))
    eventsKeep = events # use later

    # An empty batch
    events = ''
    send_to_ingest(gzip.compress(events.encode('utf-8')))

    # A batch with an empty NDJSON event, causes a validation error
    events = '{}\n'
    send_to_ingest(gzip.compress(events.encode('utf-8')))

    # a batch with faulty GZIPping, causes "decompression" error
    send_to_ingest(b'\x1f\x8b\x08\x00')

    # a duplicate batch error
    events = eventsKeep
    send_to_ingest(gzip.compress(events.encode('utf-8')))

    # a couple of weird event types to make a validation error (some failures, some accepted)
    events = make_success_events_sequence(ts, 1)
    events = events.replace('message_event', 'banana')
    send_to_ingest(gzip.compress(events.encode('utf-8')))

    # "system" errors can't be deliberately caused by faulty inputs, they are an internal thing.

    # Now exercise some other event types
    events = make_out_of_band_bounce_events_sequence(ts, 1)
    events += make_spam_complaint_events_sequence(ts, 1)
    events += make_delay_events_sequence(ts, 1)
    send_to_ingest(gzip.compress(events.encode('utf-8')))
