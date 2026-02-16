import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404


# Create your views here.
from room_schedules.settings import HOUR_BREAK_POINT
from room_schedules.models import Venue, Event, Room


def room_led_status(request, venue_id, room_id):
    """Return 'true' or 'false' as plain text indicating room availability."""
    room = get_object_or_404(Room, pk=room_id)
    now = datetime.datetime.now()
    is_available = not Event.objects.filter(
        room=room,
        start_time__lte=now,
        end_time__gte=now,
        cancelled=False,
    ).exists()
    return HttpResponse('true' if is_available else 'false', content_type='text/plain')


def show_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    events = Event.objects.filter(room__venue=venue, end_time__gte=datetime.datetime.now(), cancelled=False)
    current_date = (datetime.datetime.now() - datetime.timedelta(hours=HOUR_BREAK_POINT)).date()
    return render(request, "room_schedules/dashboard.html", {'events': events, 'current_date': current_date})


def show_room(request, venue_id, room_id):
    room = get_object_or_404(Room, pk=room_id)
    events = Event.objects.filter(room=room, end_time__gte=datetime.datetime.now(), cancelled=False)
    current_date = (datetime.datetime.now() - datetime.timedelta(hours=HOUR_BREAK_POINT)).date()
    return render(request, "room_schedules/dashboard.html", {'events': events, 'current_date': current_date, 'room': room})


def show_room_display(request, venue_id, room_id):
    room = get_object_or_404(Room, pk=room_id)
    now = datetime.datetime.now()
    current_date = (now - datetime.timedelta(hours=HOUR_BREAK_POINT)).date()

    # Get today's remaining events (not yet ended, not cancelled)
    events = list(
        Event.objects.filter(
            room=room,
            end_time__gte=now,
            cancelled=False,
        )
    )

    # Determine current and next event
    current_event = None
    next_event = None

    for event in events:
        if event.start_time <= now <= event.end_time:
            current_event = event
        elif event.start_time > now:
            if next_event is None:
                next_event = event

    # If there's no explicit next_event but we have a current event,
    # find the first event after the current one ends
    if current_event and next_event is None:
        for event in events:
            if event.start_time > current_event.end_time:
                next_event = event
                break

    is_available = current_event is None

    # Compute the start of the current free period (for progress bar).
    # This is the end time of the most recent event that finished before now.
    free_since = None
    if is_available:
        previous_event = (
            Event.objects.filter(
                room=room,
                end_time__lte=now,
                cancelled=False,
            )
            .order_by('-end_time')
            .first()
        )
        if previous_event:
            free_since = previous_event.end_time
        else:
            # No earlier event today — free since the start of the display day
            free_since = datetime.datetime.combine(
                current_date,
                datetime.time(HOUR_BREAK_POINT, 0),
            )

    # Timestamps for JS countdowns (as ISO strings for easy parsing)
    current_event_end_iso = current_event.end_time.isoformat() if current_event else None
    current_event_start_iso = current_event.start_time.isoformat() if current_event else None
    next_event_start_iso = next_event.start_time.isoformat() if next_event else None
    free_since_iso = free_since.isoformat() if free_since else None

    context = {
        'room': room,
        'events': events,
        'current_date': current_date,
        'current_event': current_event,
        'next_event': next_event,
        'is_available': is_available,
        'now_iso': now.isoformat(),
        'current_event_end_iso': current_event_end_iso,
        'current_event_start_iso': current_event_start_iso,
        'next_event_start_iso': next_event_start_iso,
        'free_since_iso': free_since_iso,
    }

    return render(request, "room_schedules/room_display.html", context)
