from django.contrib import admin
from django_celery_beat.admin import ClockedScheduleAdmin, CrontabScheduleAdmin, PeriodicTaskAdmin
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult
from unfold.admin import ModelAdmin


class UnfoldPeriodicTaskAdmin(ModelAdmin, PeriodicTaskAdmin):
    pass


class UnfoldCrontabScheduleAdmin(ModelAdmin, CrontabScheduleAdmin):
    pass


class UnfoldClockedScheduleAdmin(ModelAdmin, ClockedScheduleAdmin):
    pass


class UnfoldTaskResultAdmin(ModelAdmin, TaskResultAdmin):
    pass


admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, UnfoldPeriodicTaskAdmin)

admin.site.unregister(CrontabSchedule)
admin.site.register(CrontabSchedule, UnfoldCrontabScheduleAdmin)

admin.site.unregister(ClockedSchedule)
admin.site.register(ClockedSchedule, UnfoldClockedScheduleAdmin)

admin.site.unregister(IntervalSchedule)
admin.site.register(IntervalSchedule, ModelAdmin)

admin.site.unregister(SolarSchedule)
admin.site.register(SolarSchedule, ModelAdmin)

admin.site.unregister(TaskResult)
admin.site.register(TaskResult, UnfoldTaskResultAdmin)
