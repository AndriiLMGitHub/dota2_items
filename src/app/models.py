from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.


class Dota2Item(models.Model):
    EVENTS = (
        ("Buy", "buy"),
        ("Sell", "sell"),
    )

    CURRENSY = (
        ("RUB", "RUB"),
    )
    item_id = models.AutoField(primary_key=True, unique=True)
    market_hash_name = models.CharField(max_length=256)
    class_name = models.CharField(max_length=256, verbose_name="class")
    instance = models.CharField(max_length=256)
    time = models.CharField(max_length=256)
    event = models.CharField(max_length=256, choices=EVENTS)
    app = models.PositiveIntegerField()
    stage = models.CharField(max_length=256)
    for_who = models.CharField(
        max_length=256, null=True, blank=True, verbose_name="for"
    )
    # received = models.CharField(max_length=256, null=True, blank=True)
    # paid = models.CharField(max_length=256, null=True, blank=True)
    amount = models.CharField(max_length=256, null=True, blank=True)
    custom_id = models.CharField(max_length=256, null=True, blank=True)
    currency = models.CharField(max_length=256, choices=CURRENSY)

    def clean(self):
        if not self.received and not self.paid:
            raise ValidationError(
                "At least one of received or paid must have a value.")
        if self.received and self.paid:
            raise ValidationError(
                "Only one of received or paid can have a value.")

    def __str__(self):
        return self.market_hash_name


class Dota2ItemImage(models.Model):
    item_id = models.ForeignKey(
        Dota2Item, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="images/")

    def __str__(self):
        return self.item_id.market_hash_name
