from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from screens import models
from datetime import datetime
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
                'interspersed': models.PlaylistEntry(source=current_playlist.interspersed_source),
                'screen_interspersed': models.PlaylistEntry(source=screen.interspersed_source),
                "current_playlist": current_playlist.pk,
                "playlist_last_updated": current_playlist.last_updated.isoformat()
            }
            return render(request, 'screens/basic_screen.html', view_dict)
        else:
            return HttpResponse ("<meta http-equiv='refresh' content='60'/>No playlist set for this screen")
    except models.Screen.DoesNotExist:
        return HttpResponse("Requested screen not found")


def view_playlist(request, playlist_id):
    try:
        current_playlist = models.Playlist.objects.get(id=playlist_id)
        view_dict = {
            'playlist': current_playlist.get_sources(),
            'interspersed': models.PlaylistEntry(source=current_playlist.interspersed_source),
            "current_playlist": current_playlist.pk,
            "playlist_last_updated": current_playlist.last_updated.isoformat()
        }
        return render(request, 'screens/basic_screen.html', view_dict)
    except models.Playlist.DoesNotExist:
        return HttpResponse("Requested playlist not found")


def view_screen_automatic_json(request):
    screen = get_screen(request)
    return view_screen_json(request, screen.id)


def view_screen_json(request, screen_id):
    try:
        screen = models.Screen.objects.get(id=screen_id)
        if screen.schedule:
            current_playlist = screen.schedule.get_playlist()
            return JsonResponse(render_playlist_json(current_playlist, screen_interspersed=screen.interspersed_source))
        else:
            return JsonResponse({"error": "no playlist assigned to this screen"}, status=404)
    except models.Screen.DoesNotExist:
        return JsonResponse({"error": "screen doesnt exist"}, status=404)


def view_playlist_json(playlist_id):
    try:
        current_playlist = models.Playlist.objects.get(id=playlist_id)
        return JsonResponse(render_playlist_json(current_playlist))
    except models.Playlist.DoesNotExist:
        return JsonResponse({"error": "playlist doesnt exist"}, status=404)


def render_playlist_json(playlist, screen_interspersed=None):
    interspersed = []
    if playlist.interspersed_source:
        interspersed.append({"src": playlist.interspersed_source.src(), "type": playlist.interspersed_source.type})
    if screen_interspersed:
        interspersed.append(
            {"src": screen_interspersed.src(), "type": screen_interspersed.type})

    return {
        'playlist': list(map(lambda x: {"src": x.source.src(), "type": x.source.type, "duration": x.duration}, playlist.get_sources())),
        'interspersed': interspersed,
        "current_playlist": playlist.pk,
        "playlist_last_updated": playlist.last_updated.isoformat()
    }


def get_meta(request):
    screen = get_screen(request)
    playlist = screen.schedule.get_playlist()
    screen.last_seen = datetime.now()
    screen.save()
    out = {"current_playlist": playlist.pk,
           "playlist_last_updated": playlist.last_updated.isoformat()}
    return JsonResponse(out)
