from django.urls import path
from . import views

urlpatterns = [
    # Verifica que el nombre sea 'registro' para que el HTML funcione
    path('', views.registro_comerciante_view, name='registro'),

    path('plataforma/', views.plataforma_comerciante_view, name='plataforma_comerciante'),
    
    # También verifica que tengas la URL 'login' (necesaria para el redirect)
    path('login/', views.login_view, name='login'), 
]