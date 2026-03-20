from django.contrib import admin
from django.urls import include, path

from posts import views as posts_views
from uploads import views as uploads_views
from common.utils import health_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # public
    path('api/posts', posts_views.posts_list, name='posts_list'),
    path('api/posts/', include('posts.urls')),
    path('api/comments/', include('posts.comment_urls')),
    path('api/uploads/presign', uploads_views.presign_upload, name='presign_upload'),

    path('', health_check),
]
