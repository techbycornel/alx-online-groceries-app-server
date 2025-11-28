from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.permissions import IsAuthenticated


# -------------------------------
# Register User
# -------------------------------
@extend_schema(
    tags=["Authentication"],
    summary="Register a new user",
    description="Creates a new user account with a username, email, and password.",
    examples=[
        OpenApiExample(
            "Registration Example",
            value={"username": "johndoe", "email": "john@example.com", "password": "123456"},
            request_only=True
        )
    ]
)
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return Response({"message": "User registered successfully"}, status=201)

# -------------------------------
# Login User
# -------------------------------
@extend_schema(
    tags=["Authentication"],
    summary="Login a user",
    description="Authenticate a user and return JWT tokens along with user info.",
    examples=[
        OpenApiExample(
            "Login Example",
            value={"username": "johndoe", "password": "123456"},
            request_only=True
        )
    ]
)
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=200)


@extend_schema(
    tags=["Authentication"],
    summary="Protected route example",
    description="This route can only be accessed by logged-in users with a valid JWT token.",
    responses={
        200: OpenApiExample(
            "Success Example",
            value={"message": "Hello johndoe, you have access to this protected route!"},
            response_only=True
        ),
        401: OpenApiExample(
            "Unauthorized Example",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True
        )
    }
)
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": f"Hello {request.user.username}, you have access to this protected route!"
        })