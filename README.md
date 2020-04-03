
<a href="https://www.sparkpost.com"><img src="https://www.sparkpost.com/sites/default/files/attachments/SparkPost_Logo_2-Color_Gray-Orange_RGB.svg" width="200px"/></a>

[Sign up](https://app.sparkpost.com/join?plan=free-0817?src=Social%20Media&sfdcid=70160000000pqBb&pc=GitHubSignUp&utm_source=github&utm_medium=social-media&utm_campaign=github&utm_content=sign-up) for a SparkPost account and visit our [Developer Hub](https://developers.sparkpost.com) for even more content.

# sparkyIngest
[![Build Status](https://travis-ci.com/tuck1s/sparkyIngest.svg?branch=master)](https://travis-ci.com/tuck1s/sparkyIngest)

Example code for uploading events to the [SparkPost Ingest API](https://developers.sparkpost.com/api/events-ingest/):

Sequence
- Injection
- Delivery
- Initial_open
- Open
- Click

Sequence
- Injection
- Bounce

## Usage

Pre-requistes: `python3`, `pip`, `pipenv`.


```
pipenv install
pipenv shell
export SPARKPOST_API_KEY=your API key here
./send_to_ingest.py
```

Look in SparkPost "Events Search" menu and "Reports / Summary" chart.