Scrapes event data from [Oregonians United Against Profiling event site](https://orunited.org/events) and uploads them to the [SURJPDX event calendar](https://www.surjpdx.com/calendar/surj-pdx-calendar/). RSVP links are modified wherever possible to pre-populate the "Which organization recruited you?" question with "SURJ PDX".

### Setup
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Retrieving and uploading event data
```
$ scrapy runspider orunited.py -o event_data.json
```

After scraping the site of event data, you should have a file `event_data.json` in your root directory.

To upload to a google calendar, create a Google Cloud project, enable the Google Calendar API, and create Oauth credentials with read/write permission to that calendar. Download the credentials as a json file and move it to the project root.

Change the `CAL_ID` and `CRED_FILE` variables to reflect your Google Calendar ID and the name of your credentials file. Then run the script.

```
$ python calendar_events.py
```
