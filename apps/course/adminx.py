__author__ = 'hewei'
__date__ = '18-11-22'

import xadmin

from course.models import Course, Lesson, Video, CourseResource, BannerCourse
from organization.models import CourseOrg

class LessonInline(object):
    model = Lesson
    extra = 0


class CourseTesourceInline(object):
    model = CourseResource
    extra = 0


# 通过模型类的设置，可以吧一张表拆成多张表
# 通过设置方法跳转，完成跳转功能，详见course model 的 go_to 方法

class CourseAdmin(object):
    # model类中的方法也可以显示其返回值，也可以修改列标的名字 详见model中get_course_students_count 方法的设置
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'fav_nums', 'click_nums', 'image', 'add_time', 'get_course_students_count', 'go_to']
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'fav_nums', 'click_nums', 'image']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'fav_nums', 'click_nums', 'image', 'add_time']
    ordering = ['-click_nums']    # 设置默认排序
    readonly_fields = ['click_nums', 'add_time']  # 设置只读数据
    list_editable = ['degree', 'desc']
    exclude = ['fav_nums']           # 添加数据时不显示该字段 (外键显示搜索而非下拉框，需要在外键的model类增加 relfield_style = 'fk-ajax'
                                     #  所有外键连接的地方，xadmin中显示搜索框, 切记search_fields字段中必须是字符串字段
    inlines = [LessonInline, CourseTesourceInline]  # 外键显示编辑
    refresh_times = [3, 5]  # 页面几秒刷新一次
    style_fields = {'detail': 'ueditor'}  # ueditor 代替字段
    import_excel = True  # 显示导入excel插件

    def queryset(self):
        """分表操作-->过滤显示数据"""
        qs = super().queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        """在保存课程的时候统计课程机构的课程数"""
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_mums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin, self).post(request, args, kwargs)


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'fav_nums', 'click_nums', 'image', 'add_time']
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'fav_nums', 'click_nums', 'image']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'fav_nums', 'click_nums', 'image', 'add_time']
    ordering = ['-click_nums']    # 设置默认排序
    readonly_fields = ['click_nums', 'add_time']  # 设置只读数据
    exclude = ['fav_nums']           # 添加数据时不显示该字段 (外键显示搜索而非下拉框，需要在外键的model类增加 relfield_style = 'fk-ajax'
                                     # 所有外键连接的地方，xadmin中显示搜索框, 切记search_fields字段中必须是字符串字段
    inlines = [LessonInline, CourseTesourceInline]

    def queryset(self):
        """分表操作-->过滤显示数据"""
        qs = super().queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']  # course__name 在xadmin中显示外键的name字段


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson__name', 'name', 'add_time']  # lesson_name 在xadmin中显示外键的name字段


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'download', 'add_time']  # lesson_name 在xadmin中显示外键的name字段


xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)







