from django.db import transaction
from ..models.product import Product, ProductVariant, ProductMedia

@transaction.atomic
def create_category(*, name: str, parent_id: int = None) -> Product:
    from ..models.product import Category
    from django.utils.text import slugify
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while Category.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return Category.objects.create(name=name, slug=slug, parent_id=parent_id)

@transaction.atomic
def create_product(*, name: str, category_id: int = None, description: str = "", **kwargs) -> Product:
    return Product.objects.create(name=name, category_id=category_id, description=description, **kwargs)

@transaction.atomic
def create_variant(*, product: Product, sku: str, price: float, size: str = "", image_id: str = None, stock_quantity: int = 0) -> ProductVariant:
    return ProductVariant.objects.create(
        product=product, 
        sku=sku, 
        price=price, 
        size=size, 
        image_id=image_id,
        stock_quantity=stock_quantity
    )

@transaction.atomic
def add_product_media(*, product: Product, file, media_type: str = "IMAGE", sort_order: int = 0) -> ProductMedia:
    return ProductMedia.objects.create(product=product, file=file, media_type=media_type, sort_order=sort_order)

@transaction.atomic
def update_product(product: Product, **kwargs) -> Product:
    for field, value in kwargs.items():
        if hasattr(product, field):
            setattr(product, field, value)
    product.save()
    return product

@transaction.atomic
def delete_product(product: Product) -> None:
    product.delete()
