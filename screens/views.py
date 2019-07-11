from django.http import HttpResponse
from django.shortcuts import render
from screens import models
from screens.models import Source


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = request.META.get('REMOTE_ADDR')
    return ip


def view_screen(request):
    ip = get_client_ip(request)
    (screen, _) = models.Screen.objects.get_or_create(ip=ip,
                                                      defaults={'name': request.META['REMOTE_HOST'] or "Unknown Device",
                                                                'schedule': models.Schedule.get_default()})
    if screen.schedule:
        current_playlist = screen.schedule.get_playlist()
        view_dict = {
            'playlist': Source.objects.filter(playlistentry__playlist=current_playlist).order_by('playlistentry__number')
        }
        return render(request, 'screens/basic_screen.html', view_dict)
    else:
        return HttpResponse("No playlist set for this screen")
