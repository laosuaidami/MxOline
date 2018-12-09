__author__ = 'hewei'
__date__ = '18-11-23'
from django import forms
from captcha.fields import CaptchaField
from apps.users.models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})
    password = forms.CharField(required=True, min_length=6, error_messages={'required': '请输入长度大于6的密码'})


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True,  error_messages={'required': '邮箱不能为空'})
    password = forms.CharField(required=True, min_length=6, error_messages={'required': '请输入长度大于6的密码'})
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ForgetPwdForm(forms.Form):
    email = forms.EmailField(required=True,  error_messages={'required': '邮箱不能为空'})
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ResetPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=6, error_messages={'required': '请输入长度大于6的密码'})
    password2 = forms.CharField(required=True, min_length=6, error_messages={'required': '请输入长度大于6的密码'})


# class UploadImageForm(forms.Form):
#     image = forms.ImageField(required=True,  error_messages={'required': '邮箱不能为空'})
#

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    """用户个人信息修改"""
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birday', 'address', 'mobile']




