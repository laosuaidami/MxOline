"""MxOline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve

from MxOline.settings import MEDIA_ROOT
from users.views import IndexView, page_not_found, service_error

import xadmin

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^ueditor/', include('DjangoUeditor.urls')),   # 富文本相关url配置
    url(r'^captcha/', include('captcha.urls')),
    url(r'^user/', include('users.urls', namespace='users')),
    url(r'^org/', include('organization.urls', namespace='org')),
    url(r'^course/', include('course.urls', namespace='course')),
    url(r'^teacher/', include('course.urls', namespace='teacher')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),  # 配置上传文件的访问处理
    # url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),  # 配置上传文件的访问处理

]

# 全局404页面配置
hander404 = 'page_not_found'
hander500 = 'service_error'




