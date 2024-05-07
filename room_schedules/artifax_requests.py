import httplib2
import datetime
import json
import re

from room_schedules.data_chains import execute_chain, search_chains
from room_schedules.settings import BASE_ADDRESS, HOUR_BREAK_POINT
from advertising.settings import ARTIFAX_API_KEY as API_KEY


VENUE_ID = 2

INTERESTING_FIELDS = ['activity_detail', 'time', 'room_name', 'finish_time', 'organiser', 'room_id', 'event_id', 'cancelled']


def get_room_list():
    """
    :return: list of rooms
    :rtype: list of dict
    """
    h = httplib2.Http(".cache")
    url = BASE_ADDRESS + "/api/arrangements/room"
    (resp, content) = h.request(url, "GET", headers={'X-API-KEY': API_KEY})
    room_list = json.loads(content)
    return room_list


def repair_string(input_string: str):
    """ repair the encoding done to strings by artifax

    :param input_string: string to be reapired
    :return: input_string with all &#ddd;'s replaces with unicode characters
    :rtype: str
    """
    if input_string.__class__ == str:
        return re.sub("&#\d+;", lambda x: chr(int(x.group(0)[2:-1])), input_string)
    else:
        return input_string


def get_start_time(event: dict):
    """
    :param event: event to get a time for
    :return: doors time of an event if available and the start time if not
    :rtype: datetime.time
    """
    try:
        result = execute_chain(search_chains["doors_time"], event['custom_forms'])
        if result is None:
            raise ValueError
        out = datetime.datetime.strptime(result + ' ' + event['date'], "%H:%M:%S %Y-%m-%d")
    except (KeyError, IndexError, StopIteration, ValueError):
        out = datetime.datetime.strptime(event['start_time'][:-1] + ' ' + event['date'], "%H:%M:%S.%f %Y-%m-%d")
    return out


def get_finish_time(event: dict):
    """
    :param event: event to get a time for
    :return: doors finish time of an event if available and the end time if not
    :rtype: datetime.datetime
    """
    try:
        result = execute_chain(search_chains["end_time"], event['custom_forms'])
        if result is None:
            raise ValueError
        out = datetime.datetime.strptime(result + ' ' + event['date'], "%H:%M:%S %Y-%m-%d")
    except (KeyError, IndexError, StopIteration, ValueError):
        out = datetime.datetime.strptime(event['end_time'][:-1] + ' ' + event['date'], "%H:%M:%S.%f %Y-%m-%d")
    if out.time() <= datetime.time(hour=HOUR_BREAK_POINT):
        out += datetime.timedelta(days=1)
    return out


def get_event_organiser(event: dict):
    """ returns arrangements customers name unless the customer name starts with EUSA in which case
    return "Edinburgh University Students Association"

    :param event: event to get organiser for
    :return: a string for the organiser
    :rtype: str
    """
    name = event['arrangement_customer_entity_full_name']
    if name[:4].lower() == "eusa":
        name = "Edinburgh University Students Association"
    return name


def events_today(venue_id):
    """get of a list of events happening today (according to fringe time)

    :return: list of events
    :rtype: list of dict of (str, str)
    """
    now = datetime.datetime.now()
    date = now.date()
    if now.hour <= HOUR_BREAK_POINT:
        date -= datetime.timedelta(days=1)
    return events_happening_on_day(date, venue_id)


def events_happening_on_day(day: datetime.date, venue_id):
    """get a list of events happening on given day
    Uses Fringe time so days run from 04:00 -> 03:59

    :param day: day to get events for
    :return: list of events
    :rtype: list of dict of (str, str)
    """
    h = httplib2.Http(".cache")
    events = []
    try:
        base_url = BASE_ADDRESS + "/api/arrangements/event?venue_id={}&public_status=1&date=single&start_date={}"
        url = base_url.format(venue_id, day)
        (resp, content) = h.request(url, "GET", headers={'X-API-KEY': API_KEY})  # get requested days events
        if content == b'"No results"':  # replace error string with empty list
            events = []
        else:
            events = json.loads(content)
        url = base_url.format(venue_id, day + datetime.timedelta(days=1))
        (resp, content) = h.request(url, "GET", headers={'X-API-KEY': API_KEY})  # get day afters events
        if content == b'"No results"':  # replace error string with empty list
            new_events = []
        else:
            new_events = json.loads(content)
    except Exception as e:
        print("An error occurred while loading events from venue with id: {}".format(venue_id))
        print(e)
        new_events = []
    events.extend(new_events)
    list(map(lambda x: x.update({'time': get_start_time(x)}), events))  # add event time data
    lower_bound = datetime.datetime(year=day.year, month=day.month, day=day.day, hour=HOUR_BREAK_POINT)
    upper_bound = lower_bound + datetime.timedelta(days=1)

    def time_filter(event):
        return lower_bound < event['time'] <= upper_bound
    events = list(filter(time_filter, events))  # filter to get events by 'fringe time'
    list(map(lambda x: x.update({'finish_time': get_finish_time(x)}), events))  # add event finish_time data
    list(map(lambda x: x.update({'organiser': get_event_organiser(x)}), events))  # add event organiser
    list(map(lambda x: x.update({'cancelled': x['status_id'] in [7, 14]}), events))  # add cancelled info

    return events


def simplify_events(events):
    """simplifies events to interesting fields

    :param events: list fo events to simplify
    :type events: list of dict
    :return: simplified list of events
    :rtype: list of dict
    """
    simplified_events = []
    for event in events:
        e = {key: repair_string(event[key]) for key in INTERESTING_FIELDS}
        simplified_events.append(e)
    return simplified_events


def get_todays_events_simple(venue_id, sorted_output=False):
    """
    :return: list of simplified events in order of start time
    :rtype: list of dict
    """
    events = events_today(venue_id)
    simplified = simplify_events(events)
    if sorted_output:
        return sorted(simplified, key=lambda k: k['time'])
    return simplified
