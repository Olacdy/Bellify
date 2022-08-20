from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel

nb = dict(null=True, blank=True)


class CreateTracker(PolymorphicModel):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class CreateUpdateTracker(CreateTracker):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(CreateTracker.Meta):
        abstract = True


class GetOrNoneManager(PolymorphicManager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


class IsLivestreaming(admin.SimpleListFilter):
    title = 'Is livestreaming'
    parameter_name = 'is_livestreaming'

    def lookups(self, request, model_admin):
        return (
            ('live', 'Yes'),
            ('offline', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'live':
            return queryset.filter(livestream__isnull=False).distinct()
        elif self.value() == 'offline':
            return queryset.filter(livestream__isnull=True)


class IsEnded(admin.SimpleListFilter):
    title = 'Is livestream ended'
    parameter_name = 'is_ended'

    def lookups(self, request, model_admin):
        return (
            ('ended', 'Yes'),
            ('live', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'ended':
            return queryset.filter(livestream__ended_at__isnull=False).distinct()
        elif self.value() == 'live':
            return queryset.filter(livestream__ended_at__isnull=True)


class IsDeletingLivestreams(admin.SimpleListFilter):
    title = 'Is deleting streams'
    parameter_name = 'is_deleting_streams'

    def lookups(self, request, model_admin):
        return (
            ('deleting', 'Yes'),
            ('not_deleting', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'deleting':
            return queryset.filter(deleted_livestreams__gt=0).distinct()
        elif self.value() == 'not_deleting':
            return queryset.filter(deleted_livestreams__lt=1)
