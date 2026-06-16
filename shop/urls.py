from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from store.views import application_detail, index, car_detail, all_leased_cars, all_purchased_cars, upload_document, review_application, submit_application, create_application
from accounts.views import login_user, logout_user, signup, profile

from shop import settings

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('profile/', profile, name='profile'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('leased_offers/', all_leased_cars, name='all-leased-cars'),
    path('purchased_offers/', all_purchased_cars, name='all-purchased-cars'),
    path('car/<str:slug>/', car_detail, name='car'),
    path('car/<str:slug>/create/', create_application, name='create-application'),
    path('application/<int:application_id>/submit/', submit_application, name='submit-application'),
    path('application/', application_detail, name='application-detail'),
    path('application/<int:application_id>/upload/', upload_document, name='upload-document'),
    path('application/<int:application_id>/review/', review_application, name='review-application'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
