__author__ = 'hewei'
__date__ = '18-11-25'
import re

from django import forms
from operation.models import UserAsk


# class UserAskForm(forms.Form):
#     name = forms.CharField(required=True, min_length=2, max_length=20)
#     mobile = forms.CharField(required=True, min_length=11, max_length=11)
#     course_name= forms.CharField(required=True, min_length=2, max_length=50)


class UserAskForm(forms.ModelForm):
    # my_filed = forms.CharField()

    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):  # 要注意命名规则
        """
        验证手机号码是否合法
        :return: mobile
        """
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = r"^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError('手机号码非法', code='mobile_invalid')







