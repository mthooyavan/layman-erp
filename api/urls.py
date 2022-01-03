# pylint: disable=invalid-name
from django.urls import re_path, path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# pylint: disable=invalid-name
router = routers.SimpleRouter()

schema = get_schema_view(
    openapi.Info(
        title="Layman ERP API",
        default_version='v1',
        description="API to manage the Layman ERP platform",
        x_logo={
            "url": "",
            "backgroundColor": "#FFFFFF",
            "altText": "Layman ERP logo",
        },
    ),
    urlconf='api.urls',
    public=True,
    permission_classes=(permissions.IsAuthenticated,)
)

urlpatterns = [
    re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema.without_ui(cache_timeout=0), name='schema_json'),
    path('api/v1/', schema.with_ui('swagger', cache_timeout=0), name='schema_swagger_ui'),
    path('api/v1/docs', schema.with_ui('redoc', cache_timeout=0), name='schema_redoc'),

    path('api/v1/', include(router.urls)),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
