from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import resolve, Resolver404
from urllib.parse import urlparse
from screens import models
from django.utils import timezone
from advertising.settings import AUTO_MAKE_SCREENS_FOR_NEW_IPS, USE_LAST_FORWARDED_FOR_IP, USE_FIRST_FORWARDED_FOR_IP
import socket

def get_client_ip(request):
    if USE_LAST_FORWARDED_FOR_IP:
        return request.META.get('HTTP_X_FORWARDED_FOR').split(",")[-1].strip()
    if USE_FIRST_FORWARDED_FOR_IP:
        return request.META.get('HTTP_X_FORWARDED_FOR').split(",")[0].strip()
    ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0] or "Unknown Device"
    except socket.error:
        return "Unknown Device"


def get_screen(request):
    try:
        referer_match = resolve(urlparse(request.META.get("HTTP_REFERER", "http://example.com/"))[2])
    except Resolver404 as e:
        referer_match = None
    if referer_match and referer_match.url_name == "screens/screen_view":
        return get_object_or_404(models.Screen, id=referer_match.kwargs["screen_id"])

    # screen is from the auto url
    if AUTO_MAKE_SCREENS_FOR_NEW_IPS:
        ip = get_client_ip(request)
        (screen, _) = models.Screen.objects.get_or_create(ip=ip,
                                                          defaults={'name': get_client_hostname(ip),
                                                                    'schedule': models.Schedule.get_default()})
    else:
        ip = "255.255.255.255"
        (screen, _) = models.Screen.objects.get_or_create(ip=ip, name="DEFAULT",
                                                          defaults={'name': "DEFAULT",
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
                "current_playlist": current_playlist.pk,
                "playlist_last_updated": timezone.localtime(current_playlist.last_updated).isoformat(),
                "screen_id": screen_id,
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
            "current_playlist": current_playlist.pk,
            "playlist_last_updated": timezone.localtime(current_playlist.last_updated).isoformat()
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
            return JsonResponse(render_playlist_json(current_playlist, screen=screen, screen_id=screen_id))
        else:
            return JsonResponse({"error": "no schedule assigned to this screen"}, status=404)
    except models.Screen.DoesNotExist:
        return JsonResponse({"error": "screen doesnt exist"}, status=404)


def view_playlist_json(request, playlist_id):
    try:
        current_playlist = models.Playlist.objects.get(id=playlist_id)
        return JsonResponse(render_playlist_json(current_playlist))
    except models.Playlist.DoesNotExist:
        return JsonResponse({"error": "playlist doesnt exist"}, status=404)


def serialize_entries(entries):
    return [{"src": e.source.src(), "type": e.source.type, "duration": e.duration} for e in entries]


def aggregate_last_updated(playlist, screen=None):
    candidates = [playlist.last_updated]
    if playlist.interspersed_playlist:
        candidates.append(playlist.interspersed_playlist.last_updated)
    if screen:
        candidates.append(screen.last_updated)
        if screen.interspersed_playlist:
            candidates.append(screen.interspersed_playlist.last_updated)
    return max(candidates)


def _interspersed_stream(playlist, rate):
    if not playlist:
        return None
    items = serialize_entries(playlist.get_sources())
    if not items:
        return None
    return {"items": items, "rate": max(1, rate)}


def render_playlist_json(playlist, screen=None, screen_id=None):
    return {
        'playlist': serialize_entries(playlist.get_sources()),
        'interspersed': {
            "playlist": _interspersed_stream(playlist.interspersed_playlist, playlist.interspersed_rate),
            "screen": _interspersed_stream(screen.interspersed_playlist, screen.interspersed_rate) if screen else None,
        },
        "current_playlist": playlist.pk,
        "playlist_last_updated": timezone.localtime(aggregate_last_updated(playlist, screen)).isoformat(),
        "screen_id": screen_id
    }


def view_playlist_tree_json(request):
    playlists = models.Playlist.objects.prefetch_related("children_list").annotate(
        source_count=Count("playlistentry")
    )
    out = {}
    for pl in playlists:
        out[pl.id] = {
            "name": pl.name,
            "description": pl.description,
            "source_count": pl.source_count,
            "children": list(pl.children_list.values_list("inheriting_list_id", flat=True)),
        }
    return JsonResponse(out)


def _get_meta(request, screen):
    if screen.schedule is None:
        return JsonResponse({"error": "no schedule assigned to this screen"}, status=404)

    playlist = screen.schedule.get_playlist()
    screen.last_seen = timezone.now()
    screen.save(update_fields=["last_seen"])
    out = {"current_playlist": playlist.pk,
           "playlist_last_updated": timezone.localtime(aggregate_last_updated(playlist, screen)).isoformat()}
    return JsonResponse(out)


def get_meta(request):
    screen = get_screen(request)
    return _get_meta(request, screen)


def get_meta_screen(request, screen_id):
    screen = models.Screen.objects.get(id=screen_id)
    return _get_meta(request, screen)
