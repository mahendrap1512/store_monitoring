from rest_framework.routers import SimpleRouter
from main.views import StoreReportViewSet

router = SimpleRouter()
router.register('', StoreReportViewSet, basename='store_report')

urlpatterns = router.urls
