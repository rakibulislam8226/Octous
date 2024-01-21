from django.contrib import admin

from threadio.models import Thread, ChatGroup, ThreadRead, ChatGroupParticipant


class ThreaReadInline(admin.TabularInline):
    model = ThreadRead
    extra = 1


class ChatGroupParticipantInline(admin.TabularInline):
    model = ChatGroupParticipant
    extra = 1


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    model = Thread
    list_display = ("uid", "sender", "group")
    inlines = [ThreaReadInline]


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    model = ChatGroup
    list_display = ("uid", "name", "status")
    inlines = [ChatGroupParticipantInline]
