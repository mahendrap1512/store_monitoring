from django.db import models


class StoreStatus(models.Model):
    class StoreStatusEnum(models.TextChoices):
        ACTIVE = ("active",)
        INACTIVE = "inactive"

    store_id = models.PositiveBigIntegerField(db_index=True)
    status = models.CharField(max_length=10, choices=StoreStatusEnum.choices)
    timestamp_utc = models.DateTimeField()


class BusinessHours(models.Model):
    store_id = models.PositiveBigIntegerField(db_index=True)
    day = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()


class Timezones(models.Model):
    store_id = models.PositiveBigIntegerField(db_index=True)
    timezone_str = models.CharField(max_length=100)
