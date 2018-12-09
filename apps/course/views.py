from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from course.models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCoures
from utils.mixin_utils import LoginRequiredMixin


# Create your views here.
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = all_courses.order_by('-click_nums')[:3]
        # 课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)
                                             | Q(desc__icontains=search_keywords)
                                             | Q(detail__icontains=search_keywords))

        # 课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')
            elif sort == 'students':
                all_courses = all_courses.order_by('-students')

        # 对课程行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_courses, 6, request=request)
        courses = p.page(page)
        return render(request, 'course/course-list.html', {
            # 'all_courses': all_courses,
            'all_courses': courses,
            'hot_courses': hot_courses,
            'sort': sort,
        })


class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True


        relate_coures = []
        tag = course.tag
        if tag:
            relate_coures = Course.objects.filter(tag=tag)[:2]
        return render(request, 'course/course-detail.html', {
            'course': course,
            'relate_coures': relate_coures,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })


def get_other_student_course(course):
    """
    获取用户课程和学过该课程的用户，学过其它的所有课程
    :param course_id: 课程id
    :param course: 课程
    :return: relate_course 相关课程
    """
    user_courses = UserCoures.objects.filter(course=course)
    user_ids = [user_course.user.id for user_course in user_courses]
    all_user_course = UserCoures.objects.filter(user_id__in=user_ids)
    # 取出所有课程的id
    course_ids = [user_course.course.id for user_course in all_user_course if
                  user_course.course.id != course.id]
    # 获取学过该用户同学学过其他的所有课程
    relate_course = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
    return relate_course


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        self.add_course_2_usercoures(request, course)
        # 取学过该用户同学学过其他的所有课程
        relate_course = get_other_student_course(course)
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course/course-video.html', {
            'course': course,
            'course_resources': all_resources,
            'current_page': 'lesson',
            'relate_courses': relate_course,
        })

    @staticmethod
    def add_course_2_usercoures(request, course):
        """讲课程添加到用户课程表中"""
        # 查询用户是否已经关联了该课程
        use_courses = UserCoures.objects.filter(user=request.user, course=course)
        if not use_courses:
            use_courses = UserCoures(user=request.user, course=course)
            use_courses.save()


class CourseCommentsView(LoginRequiredMixin, View):
    """
    课程评论
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        relate_course = get_other_student_course(course)
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, 'course/course-comment.html', {
            'course': course,
            'course_resources': all_resources,
            'all_comments': all_comments,
            'current_page': 'comments',
            'relate_courses': relate_course,
        })


class AddCommentsView(View):
    """添加课程评论"""
    def post(self, request):
        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg": "用户未登录"}', content_type='application/json')
        course_id = int(request.POST.get('course_id', 0))
        comments = request.POST.get('comments', '')
        if course_id > 0 and comments:
            course_comments = CourseComments()
            try:
                course = Course.objects.get(id=course_id)
                course_comments.course = course
                course_comments.comments = comments
                course_comments.user = request.user
                course_comments.save()
                return HttpResponse('{"status":"success", "msg": "添加成功"}', content_type='application/json')
            except Course.DoesNotExist as e:
                return HttpResponse('{"status":"fail", "msg": "输入信息有误"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg": "添加失败"}', content_type='application/json')


class VideoPlayView(View):
    """"""
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        self.add_course_2_usercoures(request, course)
        # 取学过该用户同学学过其他的所有课程
        relate_course = get_other_student_course(course)
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course/course-play.html', {
            'course': course,
            'course_resources': all_resources,
            'current_page': 'lesson',
            'relate_courses': relate_course,
            'video': video,
        })

    @staticmethod
    def add_course_2_usercoures(request, course):
        """讲课程添加到用户课程表中"""
        # 查询用户是否已经关联了该课程
        use_courses = UserCoures.objects.filter(user=request.user, course=course)
        if not use_courses:
            use_courses = UserCoures(user=request.user, course=course)
            use_courses.save()


