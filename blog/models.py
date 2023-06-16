from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings  # Importa settings
from datetime import datetime

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Actualiza esta línea
    user_participation = models.IntegerField(default=0)
    title = models.CharField(max_length=250, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    evaluation = models.DecimalField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=False, null=False, default=1, decimal_places=1, max_digits=3)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    where_to_find = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    comment_text = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.comment_text


class Evaluation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='evaluations', on_delete=models.CASCADE)
    rating = models.DecimalField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1, decimal_places=1, max_digits=3)

    class Meta:
        unique_together = ('author', 'post')  # Esta línea garantiza que la combinación de author y post sea única

    def __str__(self):
        return f"{self.rating} - {self.post.title}"

