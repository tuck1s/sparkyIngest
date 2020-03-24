# sparkyIngest


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