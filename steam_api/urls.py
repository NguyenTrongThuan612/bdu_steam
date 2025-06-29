from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from steam_api.views.app.auth import AppAuthView
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
from steam_api.views.web.user import UserView
from steam_api.views.web.course_registration import WebCourseRegistrationView
from steam_api.views.web.student_registration import WebStudentRegistrationView
from steam_api.views.app.student_registration import AppStudentRegistrationView
from steam_api.views.health import HealthCheckView

app_router = SimpleRouter(trailing_slash=False)
app_router.register('auth', AppAuthView, "app_auth")
app_router.register('student-registrations', AppStudentRegistrationView, "app_student_registrations")

web_router = SimpleRouter(trailing_slash=False)
web_router.register('root', RootView, "web_user")
web_router.register('auth', WebAuthView, "web_auth")
web_router.register('users', UserView, "users")
web_router.register('courses', WebCourseView, "courses")
web_router.register('lessons', WebLessonView, "lessons")
web_router.register('classes', WebClassRoomView, "classes")
web_router.register('students', WebStudentView, "students")
web_router.register('lesson-galleries', WebLessonGalleryView, "lesson_galleries")
web_router.register('course-modules', WebCourseModuleView, "course_modules")
web_router.register('lesson-evaluations', WebLessonEvaluationView, "lesson_evaluations")
web_router.register('course-registrations', WebCourseRegistrationView, "course_registrations")
web_router.register('student-registrations', WebStudentRegistrationView, "web_student_registrations")

urlpatterns = [
   path('app/', include(app_router.urls)),
   path('back-office/', include(web_router.urls)),
   path('back-office/evaluation-criteria', EvaluationCriteriaView.as_view(), name='evaluation_criteria'),
   path('health/', HealthCheckView.as_view(), name='health-check'),
]