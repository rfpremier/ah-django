from django.db import models
from authors.apps.authentication.models import User


class Articles(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    body = models.TextField()
    image_url = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def get_readonly_fields(self, request, obj):
        if obj:
            return ["author"]
        else:
            return []