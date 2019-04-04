from django.db import models
from django.utils.text import slugify
from authors.apps.authentication.models import User


from authors.apps.utils.slug_generator import Slug


class Articles(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    body = models.TextField()
    image_url = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = Slug().generate_unique_slug(Articles, self.title)
        else:  # create
            self.slug = Slug().generate_unique_slug(Articles, self.title)
        super().save(*args, **kwargs)