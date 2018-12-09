from datetime import datetime
import json

from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from apps.users.models import UserProfile, EmailVerifyRecord, Banner
from apps.users.forms import LoginForm, RegisterForm, ForgetPwdForm, ResetPwdForm, UploadImageForm, UserInfoForm
from apps.utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCoures, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from course.models import Course
# Create your views here.


class CustomBackend(ModelBackend):
    """通过配置setting"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            # user = UserProfile.objects.get(username=username)

            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):

    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': '邮箱未激活', 'login_form': login_form})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class LogoutView(View):
    """
    用户退出登录
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get('email', '')
            pass_word = request.POST.get('password', '')
            if UserProfile.objects.filter(email=email):
                return render(request, 'register.html', {'msg': '用户已经存在', 'register_form': register_form})
            user_profile = UserProfile()
            user_profile.username = email
            user_profile.email = email
            user_profile.password = make_password(pass_word)
            user_profile.is_active = False
            user_profile.save()
            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册慕学在线网'
            user_message.save()

            send_register_email(email, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'register_form': register_form})


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                all_records.delete()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetPwdForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            if UserProfile.objects.filter(email=email):
                send_register_email(email=email, send_type='forget')     # 发送
                return render(request, 'reset_send_success.html')
            else:
                return render(request, 'forgetpwd.html', {'msg': '用户不存在', 'forget_form': forget_form})

        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    def get(self, request, active_code):
        record = EmailVerifyRecord.objects.filter(code=active_code)
        if record:
            print('有效期判断', (datetime.now() - record[0].send_time).seconds)
            if (datetime.now() - record[0].send_time).seconds < 600:
                return render(request, 'password_reset.html', {'email': record[0].email, 'secret_key': active_code})
            else:
                return render(request, 'active_fail.html')
        else:
            return render(request, 'active_fail.html')


class ResetPwdView(View):

    def post(self, request):
        reset_form = ResetPwdForm(request.POST)
        email = request.POST.get('email', '')
        secret_key = request.POST.get('secret_key', '')
        if reset_form.is_valid():
            try:
                records = EmailVerifyRecord.objects.filter(email=email)
                for record in records:
                    if record.code == secret_key:
                        password1 = request.POST.get('password1', '')
                        password2 = request.POST.get('password2', '')
                        if password1 != password2:
                            return render(request, 'password_reset.html',
                                          {'email': email, 'reset_form': reset_form,
                                           'msg': '两次输入的密码不一样', 'secret_key': secret_key})
                        else:
                            user_profile = UserProfile.objects.get(email=email)
                            user_profile.password = make_password(password1)
                            user_profile.save()
                            record.delete()
                            return render(request, 'login.html')
            except EmailVerifyRecord.DoesNotExist as e:
                # 记录日志
                return render(request, 'password_reset.html')
        else:
            return render(request, 'password_reset.html',
                          {'email': email, 'reset_form': reset_form, 'secret_key': secret_key})

        return render(request, 'active_fail.html')


class UserInfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        return render(request, 'usercenter/usercenter-info.html')

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """
    def post(self, request):
        # 普通Form
        # image_form = UploadImageForm(request.POST, request.FILES)
        # if image_form.is_valid():
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()
        # 使用model form
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    """
    个人中心修改密码
    """
    def post(self, request):
        reset_form = ResetPwdForm(request.POST)
        if reset_form.is_valid():
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            if password1 != password2:
                return HttpResponse('{"status":"fail", "msg": "两次输入的密码不一样"}', content_type='application/json')
            user_profile = request.user
            user_profile.password = make_password(password1)
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')

        else:
            return HttpResponse(json.dumps(reset_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"status": "fail", "email": "邮箱已经存在"}', content_type='application/json')
        send_register_email(email, 'update')
        return HttpResponse('{"status": "success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """修改个人邮箱"""
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "email": "验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """我的课程"""
    def get(self, request):
        user_courses = UserCoures.objects.filter(user=request.user)
        return render(request, 'usercenter/usercenter-mycourse.html', {
            'user_courses': user_courses
        })


class MyFavOrgView(LoginRequiredMixin, View):
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter/usercenter-fav-org.html', {
            'org_list': org_list
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter/usercenter-fav-teacher.html', {
            'teacher_list': teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter/usercenter-fav-course.html', {
            'course_list': course_list
        })


class MyMessageView(LoginRequiredMixin, View):
    """
    我的消息
    """
    def get(self, request):
        all_message = UserMessage.objects.filter(user=request.user.id)
        # 用户进入个人消息后清空未读消息记录
        all_unread_message = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_message:
            unread_message.has_read = True
            unread_message.save()
        # 对教师行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_message, 10, request=request)
        messages = p.page(page)
        return render(request, 'usercenter/usercenter-message.html', {
            "messages": messages
        })


class IndexView(View):
    """慕学在线网首页"""
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False).order_by('-click_nums')[:6]
        banner_courses = Course.objects.filter(is_banner=True).order_by('-click_nums')[:3]
        course_orgs = CourseOrg.objects.all().order_by('-click_nums')[:15]
        return render(request, 'index.html', {
            "all_banners": all_banners,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs,
        })


def page_not_found(request):
    """全局404处理函数"""
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def service_error(request):
    """全局500处理函数"""
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response


class LoginUnsafaView(View):
    """
    sql注入攻击
    用户名：'or 1=1#
    """
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        user_name = request.POST.get('username', '')
        pass_word = request.POST.get('password', '')

        import MySQLdb
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='dy1010', db='mxonline', charset='utf8')
        cursor = conn.cursor()
        sql_select = "select * from users_userprofile where email='{0}' and password='{1}'".format(user_name, pass_word)
        result = cursor.execute(sql_select)
        for row in cursor.fetchall():
            # 查询到用户
            pass









