#
# A library of functions for creating SparkPost ingest events
#

import json, uuid

# Returns SparkPost formatted unique event_id, which needs to be a decimal string 0 .. (2^63-1).
# Python ints are arbitrary precision so we don't need to worry about arithmetic overflow
def uniq_event_id():
    u = uuid.uuid4().int  & 0x7fffffffffffffff # uuid4 gives us 128-bit random number, need to cut down to size
    return str(u)

# Note the ingest event type is "reception", the SparkPost event type is "injection"
def make_injection_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, recv_method='smtp'):
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
                'recv_method': recv_method,
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
def make_initial_open_event(ts, rcpt_to, uniq_msg_id, geo_ip, user_agent):
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
                'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "open", the SparkPost event type is "open"
def make_open_event(ts, rcpt_to, uniq_msg_id, geo_ip, user_agent):
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
                'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "click", the SparkPost event type is "click"
def make_click_event(ts, rcpt_to, uniq_msg_id, geo_ip, user_agent):
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
                'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "amp_initial_open", the SparkPost event type is "amp_initial_open"
def make_amp_initial_open_event(ts, rcpt_to, uniq_msg_id, geo_ip, user_agent):
    timestamp = ts.time()
    e = {
        'msys': {
            'track_event': {
                'type': 'amp_initial_open',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "amp_open", the SparkPost event type is "amp_open"
def make_amp_open_event(ts, rcpt_to, uniq_msg_id, geo_ip, user_agent):
    timestamp = ts.time()
    e = {
        'msys': {
            'track_event': {
                'type': 'amp_open',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "amp_click", the SparkPost event type is "amp_click"
def make_amp_click_event(ts, rcpt_to, uniq_msg_id, geo_ip, user_agent):
    timestamp = ts.time()
    e = {
        'msys': {
            'track_event': {
                'type': 'amp_click',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'geo_ip': geo_ip,
                'message_id': uniq_msg_id,
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'target_link_url': 'https://example.com',
                'user_agent': user_agent,
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
                'recv_method': 'smtp',                      # PowerMTA does not set this, but /documentation says it's required
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
                'delv_method': 'smtp',                      # PowerMTA does not set this, but /documentation says it's required
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


# Note the ingest event type is "rejection", the SparkPost event type is "policy_rejection"
def make_policy_rejection_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, bounce_code, bounce_reason, bounce_class, raw_reason):
    timestamp = ts.time()
    e = {
        'msys': {
            'message_event': {
                'type': 'rejection',
                'bounce_class': bounce_class,
                'error_code': bounce_code,
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'message_id': uniq_msg_id,
                'msg_from': msg_from,
                'raw_rcpt_to': rcpt_to,
                'raw_reason': bounce_reason,
                'rcpt_to': rcpt_to,
                'reason': bounce_reason,
                'recv_method': 'smtp',
                'subaccount_id': 0,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "gen_rejection", the SparkPost event type is "generation_rejection"
def make_generation_rejection_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, bounce_code, bounce_reason, bounce_class, raw_reason):
    timestamp = ts.time()
    e = {
        'msys': {
            'gen_event': {
                'type': 'gen_rejection',
                'bounce_class': bounce_class,
                'campaign_id': campaign_id,
                'error_code': bounce_code,
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                'msg_from': msg_from,
                'raw_rcpt_to': rcpt_to,
                'raw_reason': bounce_reason,
                'rcpt_to': rcpt_to,
                'reason': bounce_reason,
                'recv_method': 'rest',
                'subject': subject,
                'template_id': 'template_123456',
                'template_version': '0',
                'subaccount_id': 0,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "gen_fail", the SparkPost event type is "generation_failure"
def make_generation_failure_event(ts, msg_from, friendly_from, rcpt_to, uniq_msg_id, campaign_id, subject, sending_ip, bounce_code, bounce_reason, bounce_class, raw_reason):
    timestamp = ts.time()
    e = {
        'msys': {
            'gen_event': {
                'type': 'gen_fail',
                'campaign_id': campaign_id,
                'error_code': bounce_code,
                'event_id': uniq_event_id(),
                'friendly_from': friendly_from,
                # 'message_id': uniq_msg_id, this type of error happens without getting a message_id
                'msg_from': msg_from,
                'raw_rcpt_to': rcpt_to,
                'raw_reason': bounce_reason,
                'rcpt_to': rcpt_to,
                'reason': bounce_reason,
                'recv_method': 'rest',
                'template_id': 'template_123456',
                'template_version': '0',
                'subaccount_id': 0,
                'timestamp': str(timestamp),
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "link", the SparkPost event type is "link_unsubscribe"
def make_link_unsubscribe_event(ts, rcpt_to, uniq_msg_id, user_agent):
    timestamp = ts.time()
    e = {
        'msys': {
            'unsubscribe_event': {
                'type': 'link',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'message_id': uniq_msg_id,
                'recv_method': 'smtp',                     # marked as 'required' in /documentation output
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'


# Note the ingest event type is "list", the SparkPost event type is "list_unsubscribe"
def make_list_unsubscribe_event(ts, rcpt_to, uniq_msg_id, user_agent):
    timestamp = ts.time()
    e = {
        'msys': {
            'unsubscribe_event': {
                'type': 'list',
                'delv_method': 'smtp',                     # marked as 'required' in /documentation output
                'event_id': uniq_event_id(),
                'message_id': uniq_msg_id,
                'recv_method': 'smtp',                     # marked as 'required' in /documentation output
                'rcpt_to': rcpt_to,
                'subaccount_id': 0,
                'timestamp': str(timestamp),
                # 'user_agent': user_agent,
            }
        }
    }
    return json.dumps(e, indent=None, separators=None) + '\n'

