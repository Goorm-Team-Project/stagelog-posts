from django.contrib import admin
from django.urls import include, path

from posts import views as posts_views
from common.utils import health_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # public
    path('api/posts', posts_views.posts_list, name='posts_list'),
    path('api/posts/', include('posts.urls')),
    path('api/comments/', include('posts.comment_urls')),

    path('', health_check),
]
