from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from screens import models
import socket

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0] or "Unknown Device"
    except socket.error:
        return "Unknown Device"


def get_screen(request):
    ip = get_client_ip(request)
    (screen, _) = models.Screen.objects.get_or_create(ip=ip,
                                                      defaults={'name': get_client_hostname(ip),
                                                                'schedule': models.Schedule.get_default()})
    return screen


def view_screen(request):
    screen = get_screen(request)
    if screen.schedule:
        current_playlist = screen.schedule.get_playlist()
        view_dict = {
            'playlist': current_playlist.get_sources(),
            'interspersed': current_playlist.interspersed_source,
            "current_playlist": current_playlist.pk,
            "playlist_last_updated": current_playlist.last_updated.isoformat()
        }
        return render(request, 'screens/basic_screen.html', view_dict)
    else:
        return HttpResponse("No playlist set for this screen")


def get_meta(request):
    screen = get_screen(request)
    playlist = screen.schedule.get_playlist()
    out = {"current_playlist": playlist.pk,
           "playlist_last_updated": playlist.last_updated.isoformat()}
    return JsonResponse(out)
