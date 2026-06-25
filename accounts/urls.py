from django.urls import path
from accounts.views import login_user, logout_user, signup, profile

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('profile/', profile, name='profile'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]
