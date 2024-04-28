from django.contrib import admin
from .models import Profile, Post
from django.contrib.auth.models import Group, User
# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.unregister(Group)


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
