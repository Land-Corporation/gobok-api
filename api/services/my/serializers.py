from rest_framework import serializers

from api.models.feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['title', 'content']
