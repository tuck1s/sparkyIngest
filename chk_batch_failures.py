#!/usr/bin/env python3
#
import requests, gzip, os, argparse


def stripEnd(h, s):
    if h.endswith(s):
        h = h[:-len(s)]
    return h


# condense into a access+base_url form
def hostCleanup(host):
    if not host.startswith('https://'):
        host = 'https://' + host  # Add schema
    host = stripEnd(host, '/')
    host = stripEnd(host, '/api/v1')
    host = stripEnd(host, '/')
    return host

# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Get batch failures')
parser.add_argument('batch', help='Batch ID', type=str, nargs = '+')
args = parser.parse_args()

host = hostCleanup(os.getenv('SPARKPOST_HOST', default='api.sparkpost.com'))
url = host + '/api/v1/ingest/events'

apiKey = os.getenv('SPARKPOST_API_KEY')
if apiKey == None:
    print('Environment variable SPARKPOST_API_KEY not set - stopping.')
    exit(1)

hdrs = {
    'Authorization': apiKey,
    'Content-Type': 'application/x-ndjson',
    'Content-Encoding': 'gzip'
}

for i in args.batch:
    res = requests.get(url + '/failures/' + i, headers=hdrs)
    print('Batch "{}", check status: {}\n'.format(i, res.status_code))
    result = res.content
    if res.status_code == 200:
        try:
            decoded = gzip.decompress(result)
        except Exception as err:
            print(err)
            decoded = result
        print(decoded.decode('utf8'))
    else:
        print(res.content.decode('utf8'))
