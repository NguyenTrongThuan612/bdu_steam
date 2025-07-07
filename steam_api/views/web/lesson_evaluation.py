import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsTeacher, IsNotRoot
from steam_api.models.lesson_evaluation import LessonEvaluation
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.lesson_evaluation import (
    LessonEvaluationSerializer,
    CreateLessonEvaluationSerializer,
    UpdateLessonEvaluationSerializer
)
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebLessonEvaluationView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsTeacher()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'lesson',
                openapi.IN_QUERY,
                description='Filter by lesson ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'module',
                openapi.IN_QUERY,
                description='Filter by module ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'class_room',
                openapi.IN_QUERY,
                description='Filter by class room ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'student',
                openapi.IN_QUERY,
                description='Filter by student ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: LessonEvaluationSerializer(many=True),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def list(self, request):
        try:
            logging.getLogger().info("WebLessonEvaluationView.list params=%s", request.query_params)
            lesson_id = request.query_params.get('lesson')
            module_id = request.query_params.get('module')
            class_room_id = request.query_params.get('class_room')
            student_id = request.query_params.get('student')

            evaluations = LessonEvaluation.objects.filter(deleted_at__isnull=True)

            if request.user.role == WebUserRole.TEACHER:
                evaluations = evaluations.filter(
                    Q(lesson__module__class_room__teacher=request.user) |
                    Q(lesson__module__class_room__teaching_assistant=request.user)
                )
            
            if lesson_id:
                evaluations = evaluations.filter(lesson_id=lesson_id)
                
            if module_id:
                evaluations = evaluations.filter(lesson__module_id=module_id)
                
            if class_room_id:
                evaluations = evaluations.filter(lesson__module__class_room_id=class_room_id)
                
            if student_id:
                evaluations = evaluations.filter(student_id=student_id)
                
            evaluations = evaluations.order_by('lesson__module__sequence_number', 'lesson__sequence_number')
                
            serializer = LessonEvaluationSerializer(evaluations, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebLessonEvaluationView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateLessonEvaluationSerializer,
        responses={
            201: LessonEvaluationSerializer(),
            400: 'Bad Request - Invalid data or evaluation already exists',
            403: 'Forbidden - Not teacher of this class or lesson has not completed',
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def create(self, request):
        try:
            logging.getLogger().info("WebLessonEvaluationView.create req=%s", request.data)
            serializer = CreateLessonEvaluationSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebLessonEvaluationView.create data=%s", data)

            lesson = data['lesson']
            student = data['student']
            
            if student not in lesson.module.class_room.approved_students:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Student is not enrolled in this class"
                ).response

            if request.user not in [lesson.module.class_room.teacher, lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    status=status.HTTP_403_FORBIDDEN,
                    message="You are not the teacher of this class"
                ).response
                
            if lesson.status != 'completed':
                return RestResponse(
                    status=status.HTTP_403_FORBIDDEN,
                    message="Cannot evaluate lesson that has not completed"
                ).response
            
            if LessonEvaluation.objects.filter(
                lesson=lesson,
                student=student,
                deleted_at__isnull=True
            ).exists():
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Evaluation for this student in this lesson already exists"
                ).response

            evaluation = serializer.save()
            response_serializer = LessonEvaluationSerializer(evaluation)
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebLessonEvaluationView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateLessonEvaluationSerializer,
        responses={
            200: LessonEvaluationSerializer(),
            400: 'Bad Request',
            403: 'Forbidden - Not teacher of this class, class has ended, or lesson has not completed',
            404: 'Not Found',
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonEvaluationView.update pk=%s, req=%s", pk, request.data)
            try:
                evaluation = LessonEvaluation.objects.get(pk=pk, deleted_at__isnull=True)
            except LessonEvaluation.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            if request.user not in [evaluation.lesson.module.class_room.teacher, evaluation.lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    data={"error": "You are not the teacher of this class"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            if evaluation.lesson.module.class_room.end_date < timezone.now().date():
                return RestResponse(
                    data={"error": "Cannot update evaluation after class has ended"},
                    status=status.HTTP_403_FORBIDDEN
                ).response
                
            if evaluation.lesson.status != 'completed':
                return RestResponse(
                    data={"error": "Cannot evaluate lesson that has not completed"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            serializer = UpdateLessonEvaluationSerializer(evaluation, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebLessonEvaluationView.update data=%s", data)

            updated_evaluation = serializer.save()
            response_serializer = LessonEvaluationSerializer(updated_evaluation)
            return RestResponse(data=response_serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebLessonEvaluationView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            204: 'No Content',
            403: 'Forbidden - Not teacher of this class or class has ended',
            404: 'Not Found',
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonEvaluationView.destroy pk=%s", pk)
            try:
                evaluation = LessonEvaluation.objects.get(pk=pk, deleted_at__isnull=True)
            except LessonEvaluation.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            if request.user not in [evaluation.lesson.module.class_room.teacher, evaluation.lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    data={"error": "You are not the teacher of this class"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            if evaluation.lesson.module.class_room.end_date < timezone.now().date():
                return RestResponse(
                    data={"error": "Cannot delete evaluation after class has ended"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            evaluation.deleted_at = timezone.now()
            evaluation.save(update_fields=['deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebLessonEvaluationView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 