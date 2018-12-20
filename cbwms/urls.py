"""cbwms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""
# Django imports
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^camodels/',include('apps.camodels.urls')),
    url(r'^caengine/',include('apps.caengine.urls')),
    url('', include('apps.caui.urls')),
    #url(r'^caui/',include('apps.caui.urls')),

    # provide the most basic login/logout functionality
    url( r'^login/$',auth_views.LoginView.as_view(template_name="cbas/login.html"), name="core_login"),
    url(r'^logout/$', auth_views.LogoutView, name='core_logout'),
    #url(r'^login/$', auth_views.login, {'template_name': 'core/login.html'}, name='core_login'),
    #url(r'^logout/$', auth_views.logout, name='core_logout'),

    # enable the admin interface
    url(r'^admin/', admin.site.urls),
]
