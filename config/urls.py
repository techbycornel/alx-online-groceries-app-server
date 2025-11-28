from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API routes
    path("api/auth/", include("accounts.urls")),
    path("api/", include("core.urls")),

    # OpenAPI schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # ReDoc (optional)
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
