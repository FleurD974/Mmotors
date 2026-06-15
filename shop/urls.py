from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from store.views import application_detail, index, car_detail, upload_document, review_application, submit_application, create_application
from accounts.views import login_user, logout_user, signup, profile

from shop import settings

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('profile/', profile, name='profile'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('car/<str:slug>/', car_detail, name='car'),
    path('car/<str:slug>/create/', create_application, name='create-application'),
    path('application/<int:application_id>/submit/', submit_application, name='submit-application'),
    path('application/', application_detail, name='application-detail'),
    path('application/<int:application_id>/upload/', upload_document, name='upload-document'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
