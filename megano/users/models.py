from django.db import models
from django.contrib.auth.models import User


class Avatar(models.Model):
    src = models.ImageField(
        upload_to="app_users/avatars/user_avatars/",
        default="app_users/avatars/default.png",
        verbose_name="Ссылка",
    )
    alt = models.CharField(max_length=128, verbose_name="Описание", default="User avatar")

    class Meta:
        verbose_name = "Аватар"
        verbose_name_plural = "Аватары"

    def __str__(self) -> str:
        return self.alt


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ForeignKey(Avatar, on_delete=models.DO_NOTHING,
                               related_name="profile", verbose_name="Аватар", null=True, blank=True)
    fullName = models.CharField(null=True, blank=True, max_length=100, verbose_name="Полное имя")
    phone = models.PositiveIntegerField(null=True, blank=True, verbose_name="Телефон")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name="Баланс")

    def __str__(self) -> str:
        return self.user.username
