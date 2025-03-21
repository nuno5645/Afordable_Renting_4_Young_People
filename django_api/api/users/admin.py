from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'notification_enabled', 'created_at')
    search_fields = ('user__email', 'user__username', 'phone_number')
    list_filter = ('notification_enabled', 'created_at')
