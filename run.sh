#!/bin/bash

scrapy runspider orunited.py -o event_data.json
python calendar_events.py