from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from axes.admin import AccessLog

from .models import User, PhoneNumberVerification


admin.site.register(PhoneNumberVerification)


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = [
        "phone",
        "email",
        "special_pin",
    ]
    list_filter = UserAdmin.list_filter + ("status",)
    readonly_fields = ("slug",)
    ordering = ("-created_at",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Fields",
            {
                "fields": (
                    "phone",
                    "is_online",
                    "special_pin",
                    "slug",
                    "image",
                    "gender",
                    "status",
                    "date_of_birth",
                    "height",
                    "weight",
                    "blood_group",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "phone",
                )
            },
        ),
    ) + UserAdmin.add_fieldsets


# Block user identifiers
def show_blocked_users(modeladmin, request, queryset):
    blocked_users = AccessLog.objects.filter(response_code__in=[401, 403])
    blocked_usernames = blocked_users.values_list("username", flat=True).distinct()
    blocked_user_list = ", ".join(blocked_usernames)
    message = f"Blocked Users: {blocked_user_list}"
    modeladmin.message_user(request, message)


show_blocked_users.short_description = "Show Blocked Users"


class AccessLogAdmin(admin.ModelAdmin):
    actions = [show_blocked_users]


admin.site.unregister(AccessLog)
admin.site.register(AccessLog, AccessLogAdmin)
