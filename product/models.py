from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    artikul = models.CharField(max_length=50, unique=True)
    price = models.FloatField()
    rating = models.FloatField()
    total_quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
