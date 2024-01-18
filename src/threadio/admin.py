from django.contrib import admin
from .models import Message

# Register your models here.


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "receipient",
        "is_read",
    )
    list_filter = (
        "sender",
        "receipient",
    )
    search_fields = ("sender", "receipient")
    date_hierarchy = "created_at"
    ordering = ("created_at",)
