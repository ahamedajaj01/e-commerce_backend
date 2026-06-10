from rest_framework.views import APIView
from rest_framework import status
from core.common.responses.formatters import success_response, error_response
from apps.users.permissions import IsBackofficeStaff
from apps.catalog.selectors.product_selectors import get_backoffice_products, get_active_categories
from apps.catalog.services.product_services import create_product, create_category
from apps.catalog.api.serializers import ProductBackofficeSerializer, CategorySerializer
from apps.catalog.models.product import Category

class AdminProductView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        products = get_backoffice_products()
        serializer = ProductBackofficeSerializer(products, many=True)
        return success_response(data=serializer.data)
    
    def post(self, request):
        import json
        from apps.catalog.services.product_services import create_variant
        
        # Sanitize category_id: handle empty strings from frontend as None
        cat_id = request.data.get('category_id')
        if cat_id == "" or cat_id == "null":
            cat_id = None

        product = create_product(
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            category_id=cat_id,
            base_price=request.data.get('base_price') or 0.00,
            is_visible=str(request.data.get('is_visible', True)).lower() in ['true', '1', 't', 'y', 'yes'],
            material=request.data.get('material', ''),
            sleeve=request.data.get('sleeve', ''),
            length=request.data.get('length', ''),
            neck_line=request.data.get('neck_line', ''),
            fit=request.data.get('fit', '')
        )
        
        # Handle variants and inventory
        variants_data = request.data.get('variants', '[]')
        try:
            if isinstance(variants_data, str):
                variants = json.loads(variants_data)
            else:
                variants = variants_data

            for var in variants:
                stock_qty = int(var.get('stock_quantity', 0) or 0)
                variant_obj = create_variant(
                    product=product,
                    sku=var.get('sku', ''),
                    price=var.get('price', 0.0),
                    size=var.get('size', ''),
                    color=var.get('color', ''),
                    stock_quantity=stock_qty
                )
        except Exception as e:
            pass # Fails silently if bad JSON is passed for MVP purposes
        
        # Capture the main image from FormData if provided (Thumbnail / Listing Image)
        main_image = request.FILES.get('image')
        from apps.catalog.services.product_services import add_product_media
        
        if main_image:
            add_product_media(product=product, file=main_image, sort_order=0)

        # Capture multiple additional images if provided (Product Detail Gallery)
        additional_images = request.FILES.getlist('images')
        for idx, img_file in enumerate(additional_images, start=1):
            add_product_media(product=product, file=img_file, sort_order=idx)

        return success_response(
            data=ProductBackofficeSerializer(product).data,
            status_code=status.HTTP_201_CREATED
        )

class AdminProductDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    def get(self, request, product_id):
        from apps.catalog.models.product import Product
        from core.common.responses.formatters import error_response
        try:
            product = Product.objects.get(id=product_id)
            return success_response(data=ProductBackofficeSerializer(product).data)
        except Product.DoesNotExist:
            return error_response(message="Product not found", status_code=404)

    def patch(self, request, product_id):
        from apps.catalog.models.product import Product
        from apps.catalog.services.product_services import update_product
        from core.common.responses.formatters import error_response

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return error_response(message="Product not found", status_code=404)

        # Sanitize category_id: handle empty strings from frontend as None or keep current
        category_id = request.data.get('category_id')
        if category_id == "" or category_id == "null":
            category_id = None
        elif category_id is None:
            category_id = product.category_id

        updated_product = update_product(
            product=product,
            name=request.data.get('name', product.name),
            description=request.data.get('description', product.description),
            category_id=category_id,
            base_price=request.data.get('base_price', product.base_price) or 0.00,
            is_active=str(request.data.get('is_active', product.is_active)).lower() in ['true', '1', 't', 'y', 'yes'],
            is_visible=str(request.data.get('is_visible', product.is_visible)).lower() in ['true', '1', 't', 'y', 'yes'],
            material=request.data.get('material', product.material),
            sleeve=request.data.get('sleeve', product.sleeve),
            length=request.data.get('length', product.length),
            neck_line=request.data.get('neck_line', product.neck_line),
            fit=request.data.get('fit', product.fit)
        )

        # Handle variants update
        import json
        from apps.catalog.services.product_services import create_variant
        variants_raw = request.data.get('variants')
        if variants_raw is not None:
            try:
                if isinstance(variants_raw, str):
                    variants_list = json.loads(variants_raw)
                else:
                    variants_list = variants_raw

                # Track IDs provided in the request to identify which to KEEP
                # We filter only for valid UUIDs to ensure we don't try to match temporary frontend IDs
                import uuid
                incoming_ids = []
                for v in variants_list:
                    v_id = v.get('id')
                    if v_id:
                        try:
                            # Verify it's a valid ID (not a frontend temp UUID)
                            incoming_ids.append(uuid.UUID(str(v_id)))
                        except (ValueError, TypeError):
                            continue

                # DELETE variants that belong to this product but are NOT in the incoming list
                from apps.catalog.models.product import ProductVariant
                ProductVariant.objects.filter(product=updated_product).exclude(id__in=incoming_ids).delete()

                for var_data in variants_list:
                    var_id = var_data.get('id')
                    if var_id:
                        # Update existing variant
                        try:
                            variant_obj = ProductVariant.objects.get(id=var_id, product=updated_product)
                            variant_obj.sku = var_data.get('sku', variant_obj.sku)
                            variant_obj.price = var_data.get('price', variant_obj.price)
                            variant_obj.size = var_data.get('size', variant_obj.size)
                            variant_obj.color = var_data.get('color', variant_obj.color)
                            if 'stock_quantity' in var_data:
                                variant_obj.stock_quantity = int(var_data['stock_quantity'] or 0)
                            variant_obj.save()
                        except ProductVariant.DoesNotExist:
                            pass
                    else:
                        # New variant addition during edit
                        create_variant(
                            product=updated_product,
                            sku=var_data.get('sku', ''),
                            price=var_data.get('price', 0.0),
                            size=var_data.get('size', ''),
                            color=var_data.get('color', ''),
                            stock_quantity=int(var_data.get('stock_quantity', 0))
                        )
            except (json.JSONDecodeError, TypeError, ValueError):
                pass # Silently fail for malformed JSON/Data in MVP context

        from apps.catalog.services.product_services import add_product_media
        main_image = request.FILES.get('image')
        if main_image:
            # If they upload a new main image, it gets position 0
            add_product_media(product=updated_product, file=main_image, sort_order=0)

        additional_images = request.FILES.getlist('images')
        current_media_count = updated_product.media.count()
        for idx, img_file in enumerate(additional_images, start=current_media_count + 1):
            add_product_media(product=updated_product, file=img_file, sort_order=idx)

        return success_response(data=ProductBackofficeSerializer(updated_product).data, message="Product updated")

    def delete(self, request, product_id):
        from apps.catalog.models.product import Product
        from apps.catalog.services.product_services import delete_product
        from core.common.responses.formatters import error_response

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return error_response(message="Product not found", status_code=404)

        delete_product(product)
        return success_response(message="Product deleted successfully")


class AdminCategoryView(APIView):
    permission_classes = [IsBackofficeStaff]

    def get(self, request):
        categories = get_active_categories()
        serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        name = request.data.get('name')
        if not name:
            return error_response(message="Category name is required", status_code=400)

        category = create_category(
            name=name,
            parent_id=request.data.get('parent_id')
        )
        return success_response(
            data=CategorySerializer(category).data,
            message="Category created",
            status_code=status.HTTP_201_CREATED
        )


class AdminCategoryDetailView(APIView):
    permission_classes = [IsBackofficeStaff]

    def patch(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return error_response(message="Category not found", status_code=404)

        category.name = request.data.get('name', category.name)
        if request.data.get('parent_id') is not None:
            category.parent_id = request.data.get('parent_id')
        category.is_active = request.data.get('is_active', category.is_active)
        category.save()
        return success_response(data=CategorySerializer(category).data, message="Category updated")

    def delete(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return error_response(message="Category not found", status_code=404)

        category.delete()
        return success_response(message="Category deleted successfully")
