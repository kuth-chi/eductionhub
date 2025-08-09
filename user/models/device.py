from django.db import models
from django.contrib.auth import get_user_model


class UserDevice(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    user_agent = models.CharField(max_length=256)
    ip_prefix = models.CharField(max_length=32)
    jwt_jti = models.CharField(max_length=64, unique=True)
    last_seen = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.user_agent} - {self.ip_prefix}"
