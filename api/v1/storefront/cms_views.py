from django.db import models
from rest_framework.views import APIView
from core.common.responses.formatters import success_response
from apps.cms.selectors.cms_selectors import (
    get_active_announcements,
    get_active_navigation,
    get_homepage_sections,
    get_promotion_by_id,
    get_active_promotions
)
from apps.cms.api.serializers import (
    AnnouncementBarSerializer,
    NavigationMenuSerializer,
    HomepageSectionSerializer,
    PromotionSerializer
)

class AnnouncementListView(APIView):
    permission_classes = []
    
    def get(self, request):
        announcements = get_active_announcements()
        serializer = AnnouncementBarSerializer(announcements, many=True)
        return success_response(data=serializer.data)

class NavigationListView(APIView):
    permission_classes = []
    
    def get(self, request):
        menus = get_active_navigation()
        serializer = NavigationMenuSerializer(menus, many=True)
        return success_response(data=serializer.data)

class HomepageView(APIView):
    permission_classes = []
    
    def get(self, request):
        sections = get_homepage_sections()
        serializer = HomepageSectionSerializer(sections, many=True)
        return success_response(data={"sections": serializer.data})


class PromotionDetailView(APIView):
    permission_classes = []

    def get(self, request, pk):
        promotion = get_promotion_by_id(pk)
        if not promotion:
            return success_response(data=None, message="Promotion not found")
        
        serializer = PromotionSerializer(promotion)
        return success_response(data=serializer.data)

class PromotionListView(APIView):
    permission_classes = []

    def get(self, request):
        promotions = get_active_promotions()
        serializer = PromotionSerializer(promotions, many=True)
        return success_response(data=serializer.data)

