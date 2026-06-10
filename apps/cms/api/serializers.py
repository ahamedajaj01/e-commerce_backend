from rest_framework import serializers
import json
from ..models import (
    AnnouncementBar,
    NavigationMenu,
    NavigationItem,
    HomepageSection,
    Banner,
    Promotion,
)
from apps.catalog.api.serializers import ProductStorefrontSerializer, CategorySerializer, ProductVariantSerializer

class PromotionSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    is_visible = serializers.BooleanField(source='is_active', required=False, default=True)
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'cta_text', 'cta_link', 'image', 'category', 'category_detail', 'is_active', 'is_visible', 'products', 'product_ids', 'sort_order']

    def get_products(self, obj):
        from apps.catalog.selectors.product_selectors import get_storefront_products
        
        # Use our protected selector instead of raw filter
        explicit_products = list(obj.products.filter(is_active=True))
        if obj.category:
            cat_products = get_storefront_products({'category_id': obj.category.id})
            existing_ids = {p.id for p in explicit_products}
            for p in cat_products:
                if p.id not in existing_ids:
                    explicit_products.append(p)
                    existing_ids.add(p.id)
        
        # Apply global trending/new filters to explicit products too
        return ProductStorefrontSerializer(explicit_products, many=True).data

    def create(self, validated_data):
        product_ids = validated_data.pop('product_ids', [])
        instance = super().create(validated_data)
        if product_ids:
            instance.products.set(product_ids)
        return instance

    def update(self, instance, validated_data):
        product_ids = validated_data.pop('product_ids', None)
        instance = super().update(instance, validated_data)
        if product_ids is not None:
            instance.products.set(product_ids)
        return instance

class AnnouncementBarSerializer(serializers.ModelSerializer):
    is_visible = serializers.BooleanField(source='is_active')
    linked_product_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    linked_product = ProductStorefrontSerializer(read_only=True)
    linked_promotion_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    linked_promotion = PromotionSerializer(read_only=True)

    class Meta:
        model = AnnouncementBar
        fields = ['id', 'title', 'cta_text', 'redirect_url', 'linked_product_id', 'linked_product', 'linked_promotion_id', 'linked_promotion', 'is_visible', 'sort_order']
        
    def create(self, validated_data):
        linked_product_id = validated_data.pop('linked_product_id', None)
        linked_promotion_id = validated_data.pop('linked_promotion_id', None)
        instance = super().create(validated_data)
        if linked_product_id:
            instance.linked_product_id = linked_product_id
        if linked_promotion_id:
            instance.linked_promotion_id = linked_promotion_id
        instance.save()
        return instance

    def update(self, instance, validated_data):
        linked_product_id = validated_data.pop('linked_product_id', -1)
        linked_promotion_id = validated_data.pop('linked_promotion_id', -1)
        
        if linked_product_id != -1:
             instance.linked_product_id = linked_product_id
             
        if linked_promotion_id != -1:
             instance.linked_promotion_id = linked_promotion_id
             
        instance.save()
        return super().update(instance, validated_data)



class NavigationItemSerializer(serializers.ModelSerializer):
    """Read serializer — used for list/retrieve responses and navigation rendering."""
    label = serializers.CharField(source='title')
    href = serializers.CharField(source='linked_url', allow_blank=True, default='')
    children = serializers.SerializerMethodField()
    category_slug = serializers.CharField(source='linked_category.slug', read_only=True, allow_null=True)

    class Meta:
        model = NavigationItem
        fields = [
            'id', 'menu', 'label', 'category_slug', 'href',
            'is_active', 'is_featured', 'sort_order', 'parent', 'children'
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('sort_order')
        return NavigationItemSerializer(children, many=True).data


class NavigationItemWriteSerializer(serializers.ModelSerializer):
    """Write serializer — used for creating/updating NavigationItem objects."""
    class Meta:
        model = NavigationItem
        fields = [
            'id', 'menu', 'parent', 'title', 'linked_category', 'linked_url',
            'is_active', 'sort_order', 'is_featured'
        ]
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
            'linked_category': {'required': False, 'allow_null': True},
            'linked_url': {'required': False, 'allow_blank': True},
            'is_active': {'required': False},
            'is_featured': {'required': False},
        }


class NavigationMenuSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='title', required=False)
    title = serializers.CharField(required=False)
    items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NavigationMenu
        fields = ['id', 'name', 'title', 'slug', 'sort_order', 'items']
        extra_kwargs = {
            'slug': {'required': True},
            'sort_order': {'required': False}
        }

    def validate(self, attrs):
        # Support both 'name' and 'title' from input
        if 'title' not in attrs and 'name' in attrs:
            # name source='title' should already have put it in attrs['title']
            pass
        elif 'title' in attrs:
            # explicitly provided title
            pass
        else:
             raise serializers.ValidationError({"title": "This field is required (or use 'name')."})
        return attrs

    def get_items(self, obj):
        items = obj.items.filter(parent__isnull=True, is_active=True).order_by('sort_order')
        return NavigationItemSerializer(items, many=True).data

class BannerSerializer(serializers.ModelSerializer):
    cta_link = serializers.CharField(source='link', allow_blank=True)
    cta_text = serializers.CharField(default="")

    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'cta_link', 'cta_text', 'sort_order']

class HomepageSectionSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(source='metadata')

    class Meta:
        model = HomepageSection
        fields = ['id', 'title', 'section_type', 'data', 'sort_order']


