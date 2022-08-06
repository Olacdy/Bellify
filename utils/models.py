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
