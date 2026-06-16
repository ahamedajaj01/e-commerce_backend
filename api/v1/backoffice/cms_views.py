from rest_framework.views import APIView
from rest_framework import status
from core.common.responses.formatters import success_response, error_response
from apps.users.permissions import IsBackofficeStaff
from apps.cms.models import (
    AnnouncementBar,
    NavigationMenu,
    NavigationItem,
    HomepageSection,
    Promotion
)
from apps.cms.api.serializers import (
    AnnouncementBarSerializer,
    NavigationMenuSerializer,
    NavigationItemSerializer,
    NavigationItemWriteSerializer,
    HomepageSectionSerializer,
    PromotionSerializer
)

class AdminAnnouncementView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        announcements = AnnouncementBar.objects.all().order_by('sort_order')
        serializer = AnnouncementBarSerializer(announcements, many=True)
        return success_response(data=serializer.data)
    
    def post(self, request):
        serializer = AnnouncementBarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
        return error_response(message="Invalid data", data=serializer.errors)

class AdminAnnouncementDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def put(self, request, pk):
        try:
            announcement = AnnouncementBar.objects.get(pk=pk)
        except AnnouncementBar.DoesNotExist:
            return error_response("Announcement not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = AnnouncementBarSerializer(announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data)
        return error_response("Invalid data", data=serializer.errors)
        
    def delete(self, request, pk):
        try:
            announcement = AnnouncementBar.objects.get(pk=pk)
            announcement.delete()
            return success_response(data={"success": True}, status_code=status.HTTP_204_NO_CONTENT)
        except AnnouncementBar.DoesNotExist:
            return error_response("Announcement not found", status_code=status.HTTP_404_NOT_FOUND)

class AdminNavigationMenuView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        menus = NavigationMenu.objects.all().order_by('sort_order')
        serializer = NavigationMenuSerializer(menus, many=True)
        return success_response(data=serializer.data)
    
    def post(self, request):
        serializer = NavigationMenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
        print("NavigationMenu POST Errors:", serializer.errors)
        return error_response(message="Invalid data", data=serializer.errors)

class AdminNavigationMenuDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def put(self, request, pk):
        try:
            menu = NavigationMenu.objects.get(pk=pk)
        except NavigationMenu.DoesNotExist:
            return error_response("Menu not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = NavigationMenuSerializer(menu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data)
        return error_response("Invalid data", data=serializer.errors)

    patch = put

class AdminNavigationItemView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        items = NavigationItem.objects.all().order_by('sort_order')
        serializer = NavigationItemSerializer(items, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, 'copy') else request.data
        
        
        if 'menu_id' in data and not data.get('menu'): data['menu'] = data['menu_id']
        if 'menuId' in data and not data.get('menu'): data['menu'] = data['menuId']
        if 'label' in data and not data.get('title'): data['title'] = data['label']
        if 'linked_category_id' in data and not data.get('linked_category'): data['linked_category'] = data['linked_category_id']
        if 'linked_discovery_feed_id' in data and not data.get('linked_discovery_feed'): data['linked_discovery_feed'] = data['linked_discovery_feed_id']
        
        if data.get('parent') in ['', 'null', 'undefined']: data['parent'] = None
        if data.get('linked_category') in ['', 'null', 'undefined']: data['linked_category'] = None
        if data.get('linked_discovery_feed') in ['', 'null', 'undefined']: data['linked_discovery_feed'] = None
        if 'is_featured' in data: data['is_featured'] = str(data['is_featured']).lower() in ['true', '1']
        if 'is_active' in data: data['is_active'] = str(data['is_active']).lower() in ['true', '1']

        serializer = NavigationItemWriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
        
        print("NavigationItem POST Error:", serializer.errors)
        return error_response(message="Invalid data", data=serializer.errors)

class AdminNavigationItemDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def put(self, request, pk):
        try:
            item = NavigationItem.objects.get(pk=pk)
        except NavigationItem.DoesNotExist:
            return error_response("Navigation item not found", status_code=status.HTTP_404_NOT_FOUND)
            
        data = request.data.copy() if hasattr(request.data, 'copy') else request.data
        if 'menu_id' in data and not data.get('menu'): data['menu'] = data['menu_id']
        if 'label' in data and not data.get('title'): data['title'] = data['label']
        if 'linked_category_id' in data and not data.get('linked_category'): data['linked_category'] = data['linked_category_id']
        if 'linked_discovery_feed_id' in data and not data.get('linked_discovery_feed'): data['linked_discovery_feed'] = data['linked_discovery_feed_id']
        
        if data.get('parent') in ['', 'null', 'undefined']: data['parent'] = None
        if data.get('linked_category') in ['', 'null', 'undefined']: data['linked_category'] = None
        if data.get('linked_discovery_feed') in ['', 'null', 'undefined']: data['linked_discovery_feed'] = None
        if 'is_featured' in data: data['is_featured'] = str(data['is_featured']).lower() in ['true', '1']
        if 'is_active' in data: data['is_active'] = str(data['is_active']).lower() in ['true', '1']

        serializer = NavigationItemWriteSerializer(item, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data)
            
        print("NavigationItem PUT Error:", serializer.errors)
        return error_response("Invalid data", data=serializer.errors)
        
    def delete(self, request, pk):
        try:
            item = NavigationItem.objects.get(pk=pk)
            item.delete()
            return success_response(data={"success": True}, status_code=status.HTTP_204_NO_CONTENT)
        except NavigationItem.DoesNotExist:
            return error_response("Navigation item not found", status_code=status.HTTP_404_NOT_FOUND)

class AdminHomepageSectionView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        sections = HomepageSection.objects.all().order_by('sort_order')
        serializer = HomepageSectionSerializer(sections, many=True)
        return success_response(data=serializer.data)
    
    def post(self, request):
        serializer = HomepageSectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
        return error_response(message="Invalid data", data=serializer.errors)

class AdminHomepageSectionDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get_object(self, pk):
        try:
            return HomepageSection.objects.get(pk=pk)
        except HomepageSection.DoesNotExist:
            return None

    def put(self, request, pk):
        section = self.get_object(pk)
        if not section:
            return error_response("Section not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = HomepageSectionSerializer(section, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data)
        return error_response("Invalid data", data=serializer.errors)

    def delete(self, request, pk):
        section = self.get_object(pk)
        if not section:
            return error_response("Section not found", status_code=status.HTTP_404_NOT_FOUND)
        section.delete()
        return success_response(data={"success": True}, status_code=status.HTTP_204_NO_CONTENT)



class AdminPromotionView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        promotion_type = request.query_params.get('type')
        promotions = Promotion.objects.all().prefetch_related(
            'products__media',
            'products__variants'
        )
        
        if promotion_type:
            promotions = promotions.filter(promotion_type=promotion_type.upper())
            
        promotions = promotions.order_by('sort_order')
        serializer = PromotionSerializer(promotions, many=True)
        return success_response(data=serializer.data)
    
    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
        return error_response(message="Invalid data", data=serializer.errors)

class AdminPromotionDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def put(self, request, pk):
        try:
            promotion = Promotion.objects.prefetch_related('products').get(pk=pk)
        except Promotion.DoesNotExist:
            return error_response("Promotion not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = PromotionSerializer(promotion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data)
        return error_response("Invalid data", data=serializer.errors)
        
    patch = put

    def delete(self, request, pk):
        try:
            promotion = Promotion.objects.get(pk=pk)
            promotion.delete()
            return success_response(data={"success": True}, status_code=status.HTTP_204_NO_CONTENT)
        except Promotion.DoesNotExist:
            return error_response("Promotion not found", status_code=status.HTTP_404_NOT_FOUND)

class AdminCollectionView(APIView):
    """Metadata endpoint for sections/collections."""
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        sections = HomepageSection.objects.filter(is_active=True).order_by('sort_order')
        data = [{
            "id": str(s.id),
            "title": s.title,
            "type": s.get_section_type_display()
        } for s in sections]
        return success_response(data=data)
