__author__ = 'hewei'
__date__ = '18-11-22'

""" URL Configuration

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
from django.conf.urls import url

from apps.users.views import *

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    # url(r'^login/$', LoginUnsafaView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name='active'),
    url(r'^forget/$', ForgetPwdView.as_view(), name='forget_pwd'),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name='reset'),
    url(r'^reset_pwd/$', ResetPwdView.as_view(), name='reset_pwd'),

    url(r'^info/$', UserInfoView.as_view(), name='user_info'),
    url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),
    url(r'^mymessage/$', MyMessageView.as_view(), name='mymessage'),
    url(r'^image/upload/$', UploadImageView.as_view(), name='image_upload'),  # 用户头像上传
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name='update_pwd'),  # 用户头像上传
    url(r'^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),  # 用户头像上传
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email'),  # 用户头像上传
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name='myfav_org'),
    url(r'^myfav/teacher/$', MyFavTeacherView.as_view(), name='myfav_teacher'),
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name='myfav_course'),
]
