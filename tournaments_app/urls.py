"""imdb_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tournaments_app import auth_views, admin_views, views, tournamentsViews
from rest_framework_simplejwt.views import TokenBlacklistView



from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

# http://127.0.0.1:8000/api/imdb/movies
# movies

# http://127.0.0.1:8000/api/imdb/movies/3
# http://127.0.0.1:8000/api/imdb/movies/327

router = DefaultRouter()
# movies/ POST, GET(list)
# movies/<int:movie_id> # PUT/PATCH GET DELETE
# router.register(r'^movies/(?P<pk>[^/.]+)/actors', MovieActorSet)
# movies / movie_id /actors
# movies / movie_id /actors/actor_id

# movie_actor/movie_actor_id

print(router.urls)


# movies/234

urlpatterns = [

    path('auth/login', auth_views.LoginView.as_view()),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/refresh', TokenRefreshView.as_view()),
    path('auth/signup', auth_views.signup),
    path('auth/me', auth_views.me),
    path('auth/users', auth_views.get_users),
    path('auth/setstaff', auth_views.set_staff),
    path('auth/update', auth_views.update_user),
    path('tournament/<uuid:tournament_id>/delete_participant', admin_views.delete_participant),
    


    path('org/new', views.create_organization),
    path('tournament/create', tournamentsViews.create_tournament),
    path('tournaments/<str:tournament_type>', tournamentsViews.get_tournaments),
    path('tournaments/', tournamentsViews.get_tournaments),
    

    path('summernote/', include('django_summernote.urls')),

    path('tournament/<uuid:tournament_id>/register', views.register_participant),
    path('tournament/<uuid:tournament_id>/unregister', views.unregister_participant),
    path('tournament/<uuid:tournament_id>/checkin', views.check_in_participant),
    path('tournament/<uuid:tournament_id>/start', tournamentsViews.start_tournament),
    path('tournament/<uuid:tournament_id>', tournamentsViews.get_tournament),
    # path('tournament/<uuid>/details', views.tournament),
    # path('tournament/<uuid>/pairings', views.tournament)
]

# don't do this!
# urlpatterns.append(router.urls)

urlpatterns.extend(router.urls)
