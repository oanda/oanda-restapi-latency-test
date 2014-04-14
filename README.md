# REST API Latency Test (fxPractice)

This test will make requests against the REST API on fxPractice and store the latencies in a csv file.

### Setup

You will need python-requests: `pip install requests`

Edit the configuration in config.py with your own access token and account id.

Run `python runtests.py`. The results will be saved in a csv file.
