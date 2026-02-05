from django.db import models

class Product(models.Model):
    full_name = models.CharField(max_length=255, unique=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    memory = models.CharField(max_length=50, null=True, blank=True)
    manufacturer = models.CharField(max_length=50, null=True, blank=True)
    promo_price = models.CharField(max_length=50, null=True, blank=True)
    regular_price = models.CharField(max_length=50, null=True, blank=True)
    product_code = models.CharField(max_length=50, null=True, blank=True)
    reviews_count = models.IntegerField(default=0)
    specs = models.TextField(null=True, blank=True)
    photos = models.TextField(null=True, blank=True)
    screen_diagonal = models.CharField(max_length=20, blank=True)
    screen_resolution = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.full_name
