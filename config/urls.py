from django.urls import include, path

from posts import views as posts_views
from uploads import views as uploads_views
from common.utils import health_check

urlpatterns = [
    # public
    path('api/posts', posts_views.posts_list, name='posts_list'),
    path('api/posts/<int:event_id>/inquiry', posts_views.event_posts_list, name='event_posts_inquiry'),
    path('api/posts/<int:event_id>/write', posts_views.event_posts_create, name='event_posts_write'),
    path('api/posts/', include('posts.urls')),
    path('api/comments/', include('posts.comment_urls')),
    path('api/uploads/presign', uploads_views.presign_upload, name='presign_upload'),

    path('', health_check),
]
