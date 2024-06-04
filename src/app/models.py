from django.db import models


class Dota2Item(models.Model):
    EVENTS = (
        ("buy", "buy"),
        ("sell", "sell"),
    )

    CURRENSY = (
        ("RUB", "RUB"),
    )
    item_id = models.CharField(max_length=128)
    market_hash_name = models.CharField(max_length=256)
    class_name = models.CharField(
        max_length=256, verbose_name="class", null=True, blank=True)
    instance = models.CharField(max_length=256)
    time = models.CharField(max_length=256, null=True, blank=True)
    event = models.CharField(max_length=256, choices=EVENTS)
    app = models.PositiveIntegerField()
    stage = models.CharField(max_length=256)
    for_who = models.CharField(
        max_length=256, null=True, blank=True, verbose_name="for"
    )
    amount = models.CharField(max_length=256, null=True, blank=True)
    custom_id = models.CharField(max_length=256, null=True, blank=True)
    currency = models.CharField(max_length=256, choices=CURRENSY)

    def __str__(self):
        return self.market_hash_name


class Dota2ItemImage(models.Model):
    item_id = models.ForeignKey(
        Dota2Item, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="images/")

    def __str__(self):
        return self.item_id.market_hash_name
