__author__ = 'hewei'
__date__ = '18-11-23'

from random import Random
import uuid

from apps.users.models import EmailVerifyRecord
from django.core.mail import send_mail
from MxOline.settings import EMAIL_FROM


def generate_random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type='register'):
    email_record = EmailVerifyRecord()
    if send_type == 'update':
        code = generate_random_str(4)
    else:
        code = generate_random_str(4) + str(uuid.uuid1())   # random_str + uuid1 作为密码找回和邮箱激活
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    email_title = ''
    email_body = ''
    if send_type == 'register':
        email_title = '慕学在线网注册激活链接'
        email_body = '请点击下面的链接激活你的账号：http://192.168.206.182:8000/user/active/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'forget':
        email_title = '慕学在线网密码找回链接'
        email_body = '请点击下面的链接重置你的密码：http://192.168.206.182:8000/user/reset/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'update':
        email_title = '慕学在线网邮箱修改验证码'
        email_body = '你的邮箱验证码为：{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass


