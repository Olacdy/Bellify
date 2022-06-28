from django.core.exceptions import ObjectDoesNotExist
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from django.db import models


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
