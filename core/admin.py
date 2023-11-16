from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = (
        (None,
         {
             'classes': ('wide',),
             'fields': ('email', 'username', 'password1', 'password2'),
         },),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User information', {'fields': ('user', 'first_name', 'last_name', 'phone', 'picture',)}),
        ('User location', {'fields': ('state', 'city', 'address', 'plate',)}),
        ('Times', {'fields': ('datetime_created', 'datetime_updated')})
    )
    list_display = ('user', 'full_name',)
    autocomplete_fields = ('user',)
    ordering = ('-datetime_created',)
    search_fields = ('user__username', 'user__email')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_created', 'datetime_updated', ]
        if obj:
            readonly_fields.append('user')

        return readonly_fields

    def full_name(self, obj):
        name = f'{obj.first_name} {obj.last_name}'
        if name and not name.isspace():
            return name

        return None
