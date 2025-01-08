from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterUserView, LoginUserView, LogoutUserView, UserProfileView, LeaderBoardView, ProblemsSolvedPerDayView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("leaderboard/", LeaderBoardView.as_view(), name="leaderboard"),
    path("problems-solved-per-day/", ProblemsSolvedPerDayView.as_view(), name="problems-solved-per-day"),
]
