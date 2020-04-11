
<a href="https://www.sparkpost.com"><img src="https://www.sparkpost.com/sites/default/files/attachments/SparkPost_Logo_2-Color_Gray-Orange_RGB.svg" width="200px"/></a>

[Sign up](https://app.sparkpost.com/join?plan=free-0817?src=Social%20Media&sfdcid=70160000000pqBb&pc=GitHubSignUp&utm_source=github&utm_medium=social-media&utm_campaign=github&utm_content=sign-up) for a SparkPost account and visit our [Developer Hub](https://developers.sparkpost.com) for even more content.

# sparkyIngest
[![Build Status](https://travis-ci.com/tuck1s/sparkyIngest.svg?branch=master)](https://travis-ci.com/tuck1s/sparkyIngest)

Example code for uploading events to the [SparkPost Ingest API](https://developers.sparkpost.com/api/events-ingest/):

File [ingest](ingest.py) can be used as a library for event creation.

[send_to_ingest](send_to_ingest.py) is a script to exercise the normal message sequences and some ingest error paths too:

"Success" sequence
- Injection
- Delivery
- Initial_open
- Open
- Click

"Success" sequence with AMP engagement
- Injection
- Delivery
- AMP Initial_open
- AMP Open
- AMP Click

"Bounce" (in-band) sequence
- Injection
- Bounce

Empty batch

Batch with an empty NDJSON event, causes a validation error

Duplicate batch error

A couple of weird event types to make a validation error (some failures, some accepted)

"Out of Band" bounce sequence
- Injection
- Delivery
- Out of Band bounce

Spam Complaint sequence
- Injection
- Delivery
- Spam Complaint

Delay sequence
- Injection
- Delay

Rejection sequence
- Policy Rejection (SMTP)
- Generation Rejection (REST)
- Generation Failure (REST)

Unsubscribe sequence
- Injection
- Link Unsubscribe
- List Unsubscribe

TODO: relay_injection, relay_rejection, relay_delivery, relay_tempfail, relay_permfail, ab_test_completed, ab_test_cancelled

WONTDO: sms_status (present in API, but no longer used)

## Usage

Pre-requistes: `python3`, `pip`, `pipenv`.


```
pipenv install
pipenv shell
export SPARKPOST_API_KEY=your API key here
./send_to_ingest.py
```

API responses including batch IDs are printed on stdout.

Look in SparkPost "Events Search" menu,  "Signals Analytics / Summary" chart, and "Configuration / Signals Integration" reports.