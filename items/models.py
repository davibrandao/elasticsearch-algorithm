from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, default='Uncategorized')
    tags = models.ManyToManyField(Tag, blank=True)
    popularity_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.title