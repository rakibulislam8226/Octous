from rest_framework.serializers import ModelSerializer

from core.models import User


class UserMinSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["uid", "slug", "name", "gender", "phone", "email"]
        read_only_fields = fields
