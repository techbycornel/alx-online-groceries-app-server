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

@extend_schema(
    tags=["Authentication"],
    summary="Logout a user",
    description="Blacklist the refresh token to log out the user."
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=400)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)


from django.contrib.auth.password_validation import validate_password

@extend_schema(
    tags=["Authentication"],
    summary="Change password",
    description="Allows authenticated users to change their password."
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=400)

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"error": e.messages}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=200)


from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

@extend_schema(
    tags=["Authentication"],
    summary="User profile",
    description="Retrieve or update authenticated user profile."
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # You can send this link via email
        reset_link = f"http://yourfrontend.com/reset-password/{uid}/{token}"

        send_mail(
            "Password Reset",
            f"Use this link to reset your password: {reset_link}",
            "no-reply@yourdomain.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset link sent to email"}, status=status.HTTP_200_OK)