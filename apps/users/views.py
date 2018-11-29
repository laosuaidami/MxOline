from datetime import datetime

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password

from apps.users.models import UserProfile, EmailVerifyRecord
from apps.users.forms import LoginForm, RegisterForm, ForgetPwdForm, ResetPwdForm
from apps.utils.email_send import send_register_email
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
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg': '邮箱未激活', 'login_form': login_form})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
        else:
            return render(request, 'login.html', {'login_form': login_form})


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













