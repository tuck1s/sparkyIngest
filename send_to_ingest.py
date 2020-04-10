#!/usr/bin/env python3
#
from __future__ import print_function
import requests, gzip, json, time, uuid, os
from datetime import datetime
from ingest import *

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


#
# -----------------------------------------------------------------------------------------
#  Event sequences, with time between events
# -----------------------------------------------------------------------------------------
#
# "successful" event sequence, open/click
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
    user_agent_opens = 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)'
    user_agent_click = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'

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
        events += make_initial_open_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip, user_agent=user_agent_opens)
        events += make_open_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip, user_agent=user_agent_opens)
        events += make_click_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip, user_agent=user_agent_click)
    return events


#
# "successful" event sequence, AMP open/click
#
def make_success_events_sequence_amp(ts, n):
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
    user_agent_opens = 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)'
    user_agent_click = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'

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
        events += make_amp_initial_open_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip, user_agent=user_agent_opens)
        events += make_amp_open_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip, user_agent=user_agent_opens)
        events += make_amp_click_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, geo_ip=geo_ip, user_agent=user_agent_click)
    return events


#
# "bounce" event sequence, with time between events
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


#
# "out of band" bounce event sequence, starting with injection + delivery
#
def make_out_of_band_bounce_events_sequence(ts, n):
    msg_from = 'test@oob-bounces.test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'out of band bouncy campaign'
    subject = 'out of band bounce test email'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
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

#
# "spam_complaint" event sequence, starting with injection + delivery
#
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


#
# "delay" message sequence
#
def make_delay_events_sequence(ts, n):
    msg_from = 'test@test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'campaign that gets delayed'
    subject = 'message that gets delayed'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)
        bounce_code = '452'
        raw_reason = 'smtp;452 4.2.2 Recipient Unable to accept message - mailbox full(c2mailmx101)'
        bounce_reason = raw_reason
        bounce_class = '22' # Mailbox full
        events += make_delay_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)
    return events


#
# "rejection" message sequences of various kinds
#
def make_rejection_events_sequence(ts, n):
    msg_from = 'test@test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'campaign-rejections'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        # SMTP Policy rejections have a message_id but do not log a corresponding injection event on SparkPost
        subject = 'message that gets policy rejection (smtp)'
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        bounce_class = '25' # "Admin Failure"
        bounce_code = '550'
        raw_reason = '550 5.7.1 Unconfigured Sending Domain'
        bounce_reason = raw_reason
        events += make_policy_rejection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)

        # REST Generation Rejections do not log a corresponding injection event on SparkPost
        subject = 'message that gets generation rejection (rest)'
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()

        bounce_class = '25' # "Admin Failure"
        bounce_code = '550'
        raw_reason = '550 5.6.0 No Sending Domain found in From header'
        bounce_reason = raw_reason

        events += make_generation_rejection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)

        # REST Generation Failures do not log a corresponding injection event on SparkPost
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        bounce_code = '554'
        raw_reason = '554 5.3.3 [internal] Error while rendering part html: line 1: substitution value \'myvar\' did not exist or was null'
        bounce_reason = raw_reason

        events += make_generation_failure_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip,
            bounce_code=bounce_code, bounce_reason=bounce_reason, bounce_class=bounce_class, raw_reason=raw_reason)

    return events


#
# "unsubscribe" message sequences of various kinds
#
def make_unsubscribe_events_sequence(ts, n):
    msg_from = 'test@test.sparkpost.com' # aka Envelope From, Return-Path: address
    friendly_from = 'sp-event-agent@test.sparkpost.com'
    campaign_id = 'campaign-unsubscribe'
    sending_ip = '10.0.0.1' # example

    events = ''
    for i in range(0, n):
        subject = 'message that gets unsubscribed'
        rcpt_to = uniq_recip_localpart() + '@ingest.thetucks.com'
        uniq_msg_id = uniq_message_id()
        events += make_injection_event(ts=ts,
            msg_from=msg_from, friendly_from=friendly_from, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id,campaign_id=campaign_id,
            subject=subject, sending_ip=sending_ip)

        user_agent_click = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        events += make_link_unsubscribe_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, user_agent=user_agent_click)

        events += make_list_unsubscribe_event(ts=ts, rcpt_to=rcpt_to, uniq_msg_id=uniq_msg_id, user_agent=user_agent_click)

    return events


def send_to_ingest(compressed_events):
    print('Uploading {} bytes of gzip event data'.format(len(compressed_events)))
    res = requests.post(url, data=compressed_events, headers=hdrs)
    print(res.status_code, res.content)


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

# "wind the clock back", to allow for events spread apart in time
ts = FakeTimestamp(int(time.time()) - 10*60, 2)

events = make_success_events_sequence(ts, 1) + make_bounce_events_sequence(ts, 1)
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
events = ''
events += make_out_of_band_bounce_events_sequence(ts, 1)
events += make_spam_complaint_events_sequence(ts, 1)
events += make_delay_events_sequence(ts, 1)
events += make_success_events_sequence_amp(ts, 1) # AMP opens and clicks
events += make_rejection_events_sequence(ts, 1) # Various kinds of rejection events
send_to_ingest(gzip.compress(events.encode('utf-8')))

# Unsubscribes
events = ''
events += make_unsubscribe_events_sequence(ts, 1)
send_to_ingest(gzip.compress(events.encode('utf-8')))
