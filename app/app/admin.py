from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from .models import Detection, Stream

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    staff_fields = ('name', 'owner', 'key', 'live', 'active',)
    super_fields = ('created_at', 'updated_at',)
    readonly_fields = ('link', 'live', 'uptime', 'live_at', 'not_live_at',)
    search_fields = ('identifier','key',)
    list_display = ('name', 'owner', 'key', 'live', 'uptime', 'active',)
    list_filter = ('live', 'active',)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if request.user.is_superuser:
            return query
        return query.filter(owner=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'owner' and not request.user.is_superuser:
            kwargs['queryset'] = User.objects.filter(pk=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields + self.super_fields
        return ('active',) + self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            fields = self.staff_fields + self.super_fields
        else:
            fields = self.staff_fields

        kwargs['fields'] = fields

        kwargs['widgets'] = kwargs.get('widgets', {})
        kwargs['widgets'].update({
            'key': forms.TextInput(attrs={
                'placeholder': 'Leave blank to auto-generate',
                'class': 'vTextField',
            }),
        })

        form = super().get_form(request, obj, **kwargs)

        form.base_fields['owner'].initial = request.user

        return form

@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    staff_fields = ('detected_at', 'stream', 'mask_on', 'image',)
    super_fields = ('created_at', 'updated_at',)
    readonly_fields = ('detected_at', 'stream', 'mask_on', 'image',)
    search_fields = ('stream__identifier','stream__key',)
    autocomplete_fields = ('stream',)
    list_display = ('detected_at', 'stream', 'mask_on',)
    list_filter = ('mask_on',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields + self.super_fields
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            fields = self.staff_fields + self.super_fields
        else:
            fields = self.staff_fields
        kwargs['fields'] = fields
        return super().get_form(request, obj, **kwargs)

