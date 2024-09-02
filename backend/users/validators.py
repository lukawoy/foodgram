from rest_framework.serializers import ValidationError


class FollowSelfSubscriptionValidator:
    """Проверка подписки на самого себя."""

    def __call__(self, value):
        if value.get("following") == value.get("user"):
            raise ValidationError("Нельзя подписаться на самого себя.")
