


from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
import json

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'
MIN_TIME = "2018-09-19T17:30:00-07:00"
EVENT_DATA_JSONFILENAME = 'event_data.json'
CAL_ID = 'surjpdxcalendar@gmail.com'
CRED_FILE = 'client_secret_473016767245-1sv73a6r82gbcnkqaob9ph4dfatvjant.apps.googleusercontent.com.json'


def get_credentials():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CRED_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    return creds

def get_service():
    creds = get_credentials()
    return build('calendar', 'v3', http=creds.authorize(Http()))

def print_events(service):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=CAL_ID, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        pprint(f"{start} {event} {event.get('summary')}")

def show_event_insert_response(request_id, response, exception):
    print(response, exception)



def get_preexisting_event(gcal_event_list, body):
    def filter_func(x):
        same_start = x.get('start', {}).get('dateTime') == body.get('start',{}).get('dateTime')
        same_end = x.get('end', {}).get('dateTime') == body.get('end',{}).get('dateTime')
        same_title = x.get('summary') == body.get('summary')
        return same_start and same_end and same_title

    return ([event for event in filter(filter_func, gcal_event_list.get('items'))] or [None]).pop(0)

def insert_events(service, batch=False):

    # batch = service.new_batch_http_request()

    gcal_event_response = service.events().list(calendarId=CAL_ID, timeMin=MIN_TIME).execute()
    gcal_event_list = [] if not hasattr(gcal_event_response, 'items') else gcal_event_response['items']

    with open(EVENT_DATA_JSONFILENAME) as f:
        event_data_list = json.load(f)


    for event_data in event_data_list:
        query_param_org = event_data.get('query_param_organization')
        link_querystring = f"?{query_param_org}=SURJ%20PDX" if query_param_org else ''
        event_description = f"SIGN UP HERE: {event_data.get('link', '')}{link_querystring}\n {event_data.get('description')}"

        body = {
            "summary": event_data.get('event_name'),
            "start": {
                "dateTime": event_data.get('event_start')
            },
            "end": {
                "dateTime": event_data.get('event_end')
            },
            "htmlLink": f"{event_data.get('link', '')}{link_querystring}",
            "location": f"{event_data.get('location_name', '')} {event_data.get('location_addr', '')}",
            "description": event_description,
            "visibility": "public"
        }
        preexisting_event = get_preexisting_event(gcal_event_list, body)

        if preexisting_event:
            print(f"updating preexisting event: {event_data.get('event_name')} {event_data.get('event_start')}")
            service.events().update(calendarId=CAL_ID, eventId=preexisting_event.get('id'), body=body).execute()
        else:
            print(f"inserting new event: {event_data.get('event_name')} {event_data.get('event_start')}")
            service.events().insert(calendarId=CAL_ID, body=body).execute()

        # batch.add(service.events().insert(calendarId=CAL_ID, body=body), callback=show_event_insert_response)


    # creds = get_credentials()
    # batch.execute(creds.authorize(Http()))



def main():
    """
    """
    service = get_service()

    insert_events(service)


if __name__ == '__main__':
    main()