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


def view_screen_automatic(request):
    screen = get_screen(request)
    return view_screen(request, screen.id)


def view_screen(request, screen_id):
    try:
        screen = models.Screen.objects.get(id=screen_id)
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
    except models.Screen.DoesNotExist:
        return HttpResponse("Requested screen not found")


def view_playlist(request, playlist_id):
    try:
        current_playlist = models.Playlist.objects.get(id=playlist_id)
        view_dict = {
            'playlist': current_playlist.get_sources(),
            'interspersed': current_playlist.interspersed_source,
            "current_playlist": current_playlist.pk,
            "playlist_last_updated": current_playlist.last_updated.isoformat()
        }
        return render(request, 'screens/basic_screen.html', view_dict)
    except models.Playlist.DoesNotExist:
        return HttpResponse("Requested playlist not found")



def get_meta(request):
    screen = get_screen(request)
    playlist = screen.schedule.get_playlist()
    out = {"current_playlist": playlist.pk,
           "playlist_last_updated": playlist.last_updated.isoformat()}
    return JsonResponse(out)
