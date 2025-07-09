from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from steam_api.views.app.auth import AppAuthView
from steam_api.views.app.student_registration import AppStudentRegistrationView
from steam_api.views.app.class_room import AppClassRoomView
from steam_api.views.app.course_module import AppCourseModuleView
from steam_api.views.app.lesson import AppLessonView
from steam_api.views.app.attendance import AppAttendanceView
from steam_api.views.app.lesson_gallery import AppLessonGalleryView
from steam_api.views.app.lesson_evaluation import AppLessonEvaluationView
from steam_api.views.app.course import AppCourseView
from steam_api.views.web.auth import WebAuthView
from steam_api.views.web.root import RootView
from steam_api.views.web.course import WebCourseView
from steam_api.views.web.class_room import WebClassRoomView
from steam_api.views.web.student import WebStudentView
from steam_api.views.web.lesson_gallery import WebLessonGalleryView
from steam_api.views.web.course_module import WebCourseModuleView
from steam_api.views.web.lesson_evaluation import WebLessonEvaluationView
from steam_api.views.web.evaluation_criteria import EvaluationCriteriaView
from steam_api.views.web.lesson import WebLessonView
from steam_api.views.web.user import WebUserView
from steam_api.views.web.course_registration import WebCourseRegistrationView
from steam_api.views.web.student_registration import WebStudentRegistrationView
from steam_api.views.web.attendance import WebAttendanceView
from steam_api.views.health import HealthCheckView

app_router = SimpleRouter(trailing_slash=False)
app_router.register('auth', AppAuthView, "app_auth")
app_router.register('student-registrations', AppStudentRegistrationView, "app_student_registrations")
app_router.register('classes', AppClassRoomView, "app_classes")
app_router.register('course-modules', AppCourseModuleView, "app_course_modules")
app_router.register('lessons', AppLessonView, "app_lessons")
app_router.register('attendances', AppAttendanceView, "app_attendances")
app_router.register('lesson-galleries', AppLessonGalleryView, "app_lesson_galleries")
app_router.register('lesson-evaluations', AppLessonEvaluationView, "app_lesson_evaluations")
app_router.register('courses', AppCourseView, "app_courses")

web_router = SimpleRouter(trailing_slash=False)
web_router.register('root/users', RootView, "web_root_users")
web_router.register('auth', WebAuthView, "web_auth")
web_router.register('users', WebUserView, "web_users")
web_router.register('courses', WebCourseView, "courses")
web_router.register('lessons', WebLessonView, "lessons")
web_router.register('classes', WebClassRoomView, "classes")
web_router.register('students', WebStudentView, "students")
web_router.register('lesson-galleries', WebLessonGalleryView, "lesson_galleries")
web_router.register('course-modules', WebCourseModuleView, "course_modules")
web_router.register('lesson-evaluations', WebLessonEvaluationView, "lesson_evaluations")
web_router.register('course-registrations', WebCourseRegistrationView, "course_registrations")
web_router.register('student-registrations', WebStudentRegistrationView, "web_student_registrations")
web_router.register('attendances', WebAttendanceView, "web_attendances")

urlpatterns = [
   path('app/', include(app_router.urls)),
   path('back-office/', include(web_router.urls)),
   path('back-office/evaluation-criteria', EvaluationCriteriaView.as_view(), name='evaluation_criteria'),
   path('health/', HealthCheckView.as_view(), name='health-check'),
]