from django.urls import path
from django.conf.urls import url
from . import views

# urlpatterns = [
#     path('', views.account, name=''),
#     path('/login', views.login, name='index'),
#     path('/register', views.register, name='index'),
# ]

urlpatterns = [
    url(r'^account/login/', views.login),
    url(r'^account/add/', views.add),
    url(r'^account/update/', views.update),
    url(r'^account/delete/', views.delete),
    url(r'^account/invite/accept', views.invite_accept),
    url(r'^account/', views.account),

]