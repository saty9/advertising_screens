from django.contrib import admin

# Register your models here.
from room_schedules.models import Venue, Room, Event

admin.site.register(Venue)
admin.site.register(Room)
admin.site.register(Event)