from django.db import models


class GroupChoices(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"  # active group
    BAN = "BAN", "Ban"  # group is pending for approval
    PENDING = "PENDING", "Pending"  # group is pending for approval
    REJECTED = "REJECTED", "Rejected"  # group is rejected by this app owner
    DISABLED = (
        "DISABLED",
        "Disabled",
    )  # group is disabled for being inappropriate group action


class GroupParticipantChoices(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"  # active and can message actively
    INACTIVE = (
        "INACTIVE",
        "Inactive",
    )  # this user is inactive in this group for disabled the account or something
    BLOCK = (
        "BLOCK",
        "Block",
    )  # Group owner or admin block this user to enter this group or message this group
    PENDING = (
        "PENDING",
        "Pending",
    )  # Group owner will approve this user to write message or enter the group
    REJECTED = (
        "REJECTED",
        "Rejected",
    )  # Group owner will reject the request From PENDING status
    REMOVED = (
        "REMOVED",
        "Removed",
    )  # This user will remove from this group. NO one can see this user longer
    DISABLED = (
        "DISABLED",
        "Disabled",
    )  # User might delete his account. But for reference we keep this user as DISABLED person


class GroupParticipantRoleChoices(models.TextChoices):
    OWNER = "OWNER", "Owner"
    ADMIN = "ADMIN", "Admin"
    MODERATOR = "MODERATOR", "Moderator"
    PUBLIC = "PUBLIC", "Public"


class ThreadStatusChoices(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    REMOVED = "REMOVED", "Removed"
