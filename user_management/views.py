from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserProfileSerializer


class RegisterUserView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Validate input
        if not username or not password or not email:
            return Response(
                {"error": "Missing fields", "details": "username, password, and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Conflict", "details": "The username already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        # Create the user
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
        except Exception as e:
            return Response(
                {"error": "User creation failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


class LoginUserView(APIView):
    def post(self, request):
        if request.data.get("mode") == "google":
            username = request.data.get('name')
            email = request.data.get('email')

            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(username=username, email=email)

            access_token = RefreshToken.for_user(user).access_token
            return Response(
                {
                    "message": "logged in successfully",  
                },
                status=status.HTTP_200_OK,
            )

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Both email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials, please try again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Authenticate the user
        user = authenticate(username=user.username, password=password)
        if user:
            # Generate access token only
            access_token = RefreshToken.for_user(user).access_token
            return Response(
                {
                    "token": str(access_token),  # Send only the access token
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid credentials, please try again."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

class LogoutUserView(APIView):
    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        profile = user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid input", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
