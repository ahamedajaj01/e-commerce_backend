from django.db import models
from django.utils.text import slugify
from core.common.models.base import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(BaseModel):
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products'
    )
    brand = models.ForeignKey(
        'catalog.Brand',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # New detailed product attributes
    material = models.CharField(max_length=100, blank=True)
    sleeve = models.CharField(max_length=100, blank=True)
    length = models.CharField(max_length=100, blank=True)
    neck_line = models.CharField(max_length=100, blank=True)
    fit = models.CharField(max_length=100, blank=True)
    
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductVariant(BaseModel):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants'
    )
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, blank=True) # e.g. "Red / XL"
    size = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

class ProductMedia(BaseModel):
    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "Image"

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='media'
    )
    media_type = models.CharField(
        max_length=10, 
        choices=MediaType.choices, 
        default=MediaType.IMAGE
    )
    file = models.FileField(upload_to='products/media/')
    sort_order = models.PositiveIntegerField(default=0)
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['sort_order']
        verbose_name_plural = "Product Media"
