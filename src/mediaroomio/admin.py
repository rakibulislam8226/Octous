from django.contrib import admin
from .models import MediaRoomConnector, MediaRoom

# Register your models here.
admin.site.register(MediaRoomConnector)


class MediaRoomConnectorInline(admin.TabularInline):
    model = MediaRoomConnector
    extra = 1


@admin.register(MediaRoom)
class MediaRoomAdmin(admin.ModelAdmin):
    model = MediaRoom
    list_display = ("uid",)
    inlines = [MediaRoomConnectorInline]
