import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsTeacher, IsManager
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
        return [IsManager()]

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
            logging.getLogger().info("WebLessonEvaluationView.list")
            lesson_id = request.query_params.get('lesson')
            module_id = request.query_params.get('module')
            class_room_id = request.query_params.get('class_room')
            student_id = request.query_params.get('student')
            
            evaluations = LessonEvaluation.objects.filter(
                lesson__module__class_room__teacher=request.user,
                deleted_at__isnull=True
            ) | LessonEvaluation.objects.filter(
                lesson__module__class_room__teaching_assistant=request.user,
                deleted_at__isnull=True
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
            logging.getLogger().exception("WebLessonEvaluationView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateLessonEvaluationSerializer,
        responses={
            201: LessonEvaluationSerializer(),
            400: 'Bad Request - Invalid data or evaluation already exists',
            403: 'Forbidden - Not teacher of this class',
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

            lesson = serializer.validated_data['lesson']
            student = serializer.validated_data['student']
            
            # Kiểm tra xem học viên có thuộc lớp học không
            if student not in lesson.module.class_room.students.all():
                return RestResponse(
                    data={"error": "Student is not enrolled in this class"},
                    status=status.HTTP_400_BAD_REQUEST
                ).response

            # Kiểm tra người dùng có phải là giáo viên của lớp không
            if request.user not in [lesson.module.class_room.teacher, lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    data={"error": "You are not the teacher of this class"},
                    status=status.HTTP_403_FORBIDDEN
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
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonEvaluationView.update pk=%s, req=%s", pk, request.data)
            try:
                evaluation = LessonEvaluation.objects.get(pk=pk, deleted_at__isnull=True)
            except LessonEvaluation.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            # Kiểm tra người dùng có phải là giáo viên của lớp không
            if request.user not in [evaluation.lesson.module.class_room.teacher, evaluation.lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    data={"error": "You are not the teacher of this class"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            # Kiểm tra lớp học đã kết thúc chưa
            if evaluation.lesson.module.class_room.end_date < timezone.now().date():
                return RestResponse(
                    data={"error": "Cannot update evaluation after class has ended"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            serializer = UpdateLessonEvaluationSerializer(evaluation, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

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

            # Kiểm tra người dùng có phải là giáo viên của lớp không
            if request.user not in [evaluation.lesson.module.class_room.teacher, evaluation.lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    data={"error": "You are not the teacher of this class"},
                    status=status.HTTP_403_FORBIDDEN
                ).response

            # Kiểm tra lớp học đã kết thúc chưa
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