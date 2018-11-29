__author__ = 'hewei'
__date__ = '18-11-22'


import xadmin
from .models import CityDict, CourseOrg, Teacher


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'add_time']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'image', 'address', 'city', 'add_time']
    search_fields = ['name', 'desc', 'click_nums', 'image', 'address', 'city']
    list_filter = ['name', 'desc', 'click_nums', 'image', 'address', 'city__name', 'add_time']  # city__name 在xadmin中显示外键的name字段


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company', 'points', 'click_nums', 'fav_nums', 'image', 'add_time']
    search_fields = ['org', 'name', 'work_years', 'work_company', 'points', 'click_nums', 'fav_nums', 'image']
    list_filter = ['org__name', 'name', 'work_years', 'work_company', 'points', 'click_nums', 'fav_nums', 'image', 'add_time']  # city__name 在xadmin中显示外键的name字段


xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)
