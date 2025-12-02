from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiExample


# ----------------------------
# Categories CRUD
# ----------------------------
@extend_schema(tags=["Categories"])
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@extend_schema(tags=["Categories"])
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# ----------------------------
# Products CRUD
# ----------------------------
@extend_schema(
    tags=["Products"],
    summary="List or create products",
    description="Retrieve all products or create a new product with image upload.",
    examples=[
        OpenApiExample(
            "Create Product Example",
            value={
                "name": "Laptop",
                "description": "High-end gaming laptop",
                "price": 2500.00,
                "category": 1,  # ID of category
                "image": None   # upload image as multipart/form-data
            },
            request_only=True
        )
    ]
)
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    permission_classes = [IsAuthenticatedOrReadOnly]

@extend_schema(
    tags=["Products"],
    summary="Retrieve, update, or delete a product",
    description="Get details, update info, or delete a product."
)
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
