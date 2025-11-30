# KIẾN TRÚC HỆ THỐNG CHI TIẾT

## MỤC LỤC
1. [Tổng quan kiến trúc](#tổng-quan-kiến-trúc)
2. [Layer Architecture](#layer-architecture)
3. [Database Schema](#database-schema)
4. [API Design](#api-design)
5. [Authentication Flow](#authentication-flow)
6. [File Storage](#file-storage)
7. [Caching Strategy](#caching-strategy)
8. [Logging & Monitoring](#logging--monitoring)

---

## TỔNG QUAN KIẾN TRÚC

### Mô hình kiến trúc
Hệ thống sử dụng **Monolithic Architecture** với Django REST Framework, tổ chức theo mô hình **Layered Architecture**.

### Ưu điểm của kiến trúc này
- **Đơn giản**: Dễ phát triển, deploy và maintain
- **Hiệu năng cao**: Không có overhead của microservices
- **Transactions**: Dễ dàng quản lý transactions trong database
- **Phù hợp với quy mô**: Đủ cho hệ thống quản lý học viên cỡ vừa

### Nhược điểm và cách khắc phục
- **Scalability**: Khó scale từng component riêng lẻ
  - *Giải pháp*: Sử dụng Redis caching, database optimization
- **Deployment**: Deploy toàn bộ app khi có thay đổi
  - *Giải pháp*: CI/CD pipeline, blue-green deployment

---

## LAYER ARCHITECTURE

### 1. Presentation Layer (API Layer)

#### Thành phần
- **Django REST Framework ViewSets**
- **URL Routing**
- **Swagger/OpenAPI Documentation**

#### Nhiệm vụ
- Nhận HTTP requests
- Validate request data (initial)
- Route đến đúng view/viewset
- Format response (JSON)
- Handle HTTP status codes

#### Cấu trúc
```
steam_api/views/
├── web/                 # Back-office APIs
│   ├── auth.py         # WebAuthView
│   ├── student.py      # WebStudentView
│   ├── course.py       # WebCourseView
│   └── ...
└── app/                 # Mobile APIs
    ├── auth.py         # AppAuthView
    ├── course.py       # AppCourseView
    └── ...
```

#### Ví dụ ViewSet
```python
class WebStudentView(viewsets.ModelViewSet):
    """
    API endpoints cho quản lý học viên
    """
    queryset = Student.objects.filter(deleted_at__isnull=True)
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Custom query logic
        queryset = super().get_queryset()
        # Filter, search, pagination
        return queryset
```

### 2. Business Logic Layer

#### Thành phần
- **Serializers**: Data validation & transformation
- **Middlewares**: Cross-cutting concerns
- **Helpers**: Business logic utilities

#### Serializers
**Nhiệm vụ**:
- Validate input data
- Transform data (serialize/deserialize)
- Handle nested relationships
- Custom validation rules

**Cấu trúc**:
```
steam_api/serializers/
├── student.py              # StudentSerializer
├── course.py               # CourseSerializer
├── lesson.py               # LessonSerializer
└── custom_token_*.py       # JWT serializers
```

**Ví dụ**:
```python
class StudentSerializer(serializers.ModelSerializer):
    parent_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
    
    def validate_identification_number(self, value):
        # Custom validation
        if len(value) < 9:
            raise ValidationError("Invalid ID number")
        return value
    
    def get_parent_info(self, obj):
        return {
            'name': obj.parent_name,
            'phone': obj.parent_phone,
            'email': obj.parent_email
        }
```

#### Middlewares
**Các middleware chính**:

1. **Authentication Middleware**
```python
# steam_api/middlewares/web_authentication.py
- Kiểm tra JWT token
- Load user từ token
- Gắn user vào request.user
```

2. **Permission Middleware**
```python
# steam_api/middlewares/permissions.py
- Kiểm tra quyền truy cập
- Role-based access control
- Object-level permissions
```

3. **Custom User Authentication Rule**
```python
# steam_api/middlewares/custom_user_authentication_rule.py
- Custom logic cho JWT authentication
- Support cả WebUser và AppUser
```

#### Helpers
**Business logic utilities**:

1. **Lesson Schedule Helper**
```python
# steam_api/helpers/lesson_schedule.py
def calculate_lesson_status(start_date, end_date, schedule, lesson_sequence):
    """Tính toán trạng thái buổi học"""
    
def get_lesson_start_datetime(start_date, schedule, lesson_sequence):
    """Tính thời gian bắt đầu buổi học"""
    
def get_lesson_end_datetime(start_date, schedule, lesson_sequence):
    """Tính thời gian kết thúc buổi học"""
```

2. **Storage Helpers**
```python
# steam_api/helpers/google_drive_storage.py
- Upload file lên Google Drive
- Tạo public link
- Quản lý folders

# steam_api/helpers/local_storage.py
- Upload file lên local server
- Serve static files
```

3. **Email Helper**
```python
# steam_api/helpers/send_html_email.py
- Gửi email HTML
- Template rendering
- SMTP configuration
```

4. **OTP Helper**
```python
# steam_api/helpers/otp.py
- Generate OTP code
- Store OTP in cache (Redis)
- Verify OTP
- OTP expiration
```

### 3. Data Access Layer (ORM Layer)

#### Thành phần
- **Django Models**: ORM mapping
- **Model Managers**: Custom query methods
- **Model Properties**: Computed fields

#### Models Organization
```
steam_api/models/
├── __init__.py
├── web_user.py             # Web users (admin, teacher)
├── app_user.py             # App users
├── student.py              # Students
├── course.py               # Courses
├── class_room.py           # Classes
├── course_module.py        # Course modules
├── lesson.py               # Lessons
├── attendance.py           # Attendance
├── lesson_evaluation.py    # Evaluations
├── course_registration.py  # Registrations
├── facility.py             # Facilities
└── news.py                 # News
```

#### Model Best Practices

**1. Soft Delete Pattern**
```python
class Student(models.Model):
    # ... fields ...
    deleted_at = models.DateTimeField(null=True)
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(deleted_at__isnull=True)
```

**2. Computed Properties**
```python
class ClassRoom(models.Model):
    # ... fields ...
    
    @property
    def total_sessions(self):
        """Tính tổng số buổi học"""
        return sum(
            module.total_lessons 
            for module in self.modules.filter(deleted_at__isnull=True)
        )
    
    @property
    def current_students_count(self):
        """Đếm số học viên hiện tại"""
        return self.approved_students.count()
```

**3. Custom Managers**
```python
class ActiveStudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted_at__isnull=True,
            is_active=True
        )

class Student(models.Model):
    # ... fields ...
    objects = models.Manager()  # Default manager
    active = ActiveStudentManager()  # Custom manager
```

**4. Model Validation**
```python
class Lesson(models.Model):
    # ... fields ...
    
    def clean(self):
        # Validate sequence_number is unique within module
        if Lesson.objects.filter(
            module=self.module,
            sequence_number=self.sequence_number
        ).exclude(id=self.id).exists():
            raise ValidationError("Sequence number already exists")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Call clean() before save
        super().save(*args, **kwargs)
```

### 4. Infrastructure Layer

#### Database (MySQL)
**Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'steam',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

**Optimization**:
- Connection pooling
- Query optimization (select_related, prefetch_related)
- Database indexes
- Proper use of transactions

#### Cache (Redis)
**Configuration**:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50
            }
        }
    }
}
```

**Use cases**:
- Session storage
- OTP storage (với expiration)
- Query result caching
- API response caching

#### External Services

**1. Google Drive API**
```python
# Upload file
from steam_api.helpers.google_drive_storage import GoogleDriveStorage

storage = GoogleDriveStorage()
file_url = storage.upload_file(file, filename, folder_id)
```

**2. Email Service (SMTP)**
```python
# Send email
from steam_api.helpers.send_html_email import send_html_email

send_html_email(
    subject="Welcome to STEAM",
    template="welcome.html",
    context={'name': 'John'},
    recipient_list=['user@example.com']
)
```

**3. Logging Service (BetterStack)**
```python
# Automatic logging
import logging

logger = logging.getLogger(__name__)
logger.info("User logged in", extra={'user_id': user.id})
logger.error("Error occurred", exc_info=True)
```

---

## DATABASE SCHEMA

### Relationships Overview

```
WebUser (1) ─────────┐
                     │ teacher/TA
                     ▼ (N)
Course (1) ──────► ClassRoom (1) ──────► CourseModule (1) ──────► Lesson
                     │                                              │
                     │ (N)                                          │ (N)
                     │                                              │
                     ▼                                              ▼
Student ◄──── CourseRegistration              Attendance ──────────┤
   │                                                                │
   └────────────────────────────────────────► LessonEvaluation ────┘
```

### Indexes Strategy

**Frequently queried fields**:
```sql
-- Student
CREATE INDEX idx_student_identification ON students(identification_number);
CREATE INDEX idx_student_email ON students(email);
CREATE INDEX idx_student_active ON students(is_active, deleted_at);

-- ClassRoom
CREATE INDEX idx_classroom_course ON class_rooms(course_id);
CREATE INDEX idx_classroom_teacher ON class_rooms(teacher_id);
CREATE INDEX idx_classroom_dates ON class_rooms(start_date, end_date);

-- Lesson
CREATE INDEX idx_lesson_module ON lessons(module_id);
CREATE INDEX idx_lesson_sequence ON lessons(module_id, sequence_number);

-- Attendance
CREATE INDEX idx_attendance_student ON attendances(student_id);
CREATE INDEX idx_attendance_lesson ON attendances(lesson_id);
CREATE UNIQUE INDEX idx_attendance_unique ON attendances(student_id, lesson_id);

-- LessonEvaluation
CREATE INDEX idx_evaluation_lesson ON lesson_evaluations(lesson_id);
CREATE INDEX idx_evaluation_student ON lesson_evaluations(student_id);
CREATE UNIQUE INDEX idx_evaluation_unique ON lesson_evaluations(lesson_id, student_id);
```

### Foreign Key Constraints

**Cascade Rules**:
```python
# CASCADE: Xóa parent → xóa children
course = models.ForeignKey(Course, on_delete=models.CASCADE)

# SET_NULL: Xóa parent → set children FK = NULL
teacher = models.ForeignKey(WebUser, on_delete=models.SET_NULL, null=True)

# PROTECT: Không cho xóa parent nếu còn children
# (Không dùng trong hệ thống này - dùng soft delete)
```

### Soft Delete Pattern

**Tất cả models đều có field `deleted_at`**:
```python
deleted_at = models.DateTimeField(null=True)

# Query active records
Student.objects.filter(deleted_at__isnull=True)

# Soft delete
student.deleted_at = timezone.now()
student.save()
```

**Lợi ích**:
- Không mất dữ liệu lịch sử
- Có thể restore
- Audit trail
- Maintain referential integrity

---

## API DESIGN

### RESTful Principles

**Resource-based URLs**:
```
GET    /back-office/students      → List students
POST   /back-office/students      → Create student
GET    /back-office/students/123  → Get student detail
PUT    /back-office/students/123  → Update student
DELETE /back-office/students/123  → Delete student (soft)
```

### API Versioning Strategy

**Current**: No explicit versioning (v1 by default)
**Future**: URL versioning
```
/api/v1/back-office/students
/api/v2/back-office/students
```

### Response Format

**Success Response**:
```json
{
  "id": 123,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  ...
}
```

**List Response with Pagination**:
```json
{
  "count": 150,
  "next": "http://api.example.com/students?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Student 1"
    },
    ...
  ]
}
```

**Error Response**:
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

**Validation Error Response**:
```json
{
  "field_name": [
    "Error message 1",
    "Error message 2"
  ]
}
```

### HTTP Status Codes

```
200 OK              - Successful GET, PUT
201 Created         - Successful POST
204 No Content      - Successful DELETE
400 Bad Request     - Validation error
401 Unauthorized    - Authentication required
403 Forbidden       - Permission denied
404 Not Found       - Resource not found
500 Internal Error  - Server error
```

### Filtering & Search

**Query Parameters**:
```
GET /back-office/students?search=john
GET /back-office/students?is_active=true
GET /back-office/students?gender=male
GET /back-office/students?class_room=5
GET /back-office/students?ordering=-created_at
GET /back-office/students?page=2&page_size=20
```

### Pagination

**Default**: 20 items per page
**Max**: 100 items per page

```
GET /back-office/students?page=1&page_size=50
```

---

## AUTHENTICATION FLOW

### JWT Authentication

#### Login Flow (Web)
```
1. User gửi credentials
   POST /back-office/auth/login
   { "email": "user@example.com", "password": "password" }
   
2. Server validate credentials
   - Check email exists
   - Verify password (bcrypt)
   - Check user status (activated)
   
3. Server tạo JWT tokens
   - Access token (expire: 180 minutes)
   - Refresh token (expire: 30 days)
   
4. Response với tokens
   {
     "access": "eyJ0eXAi...",
     "refresh": "eyJ0eXAi...",
     "user": { ... }
   }
   
5. Client lưu tokens
   - localStorage hoặc cookie
   - Gửi access token trong mỗi request
```

#### Authenticated Request Flow
```
1. Client gửi request với token
   GET /back-office/students
   Headers: {
     "Authorization": "Bearer eyJ0eXAi..."
   }
   
2. Middleware kiểm tra token
   - Parse JWT token
   - Verify signature
   - Check expiration
   - Load user từ token payload
   
3. Middleware kiểm tra permissions
   - Check user role
   - Check user status
   - Check object permissions
   
4. Process request
   - Execute view logic
   - Return response
```

#### Token Refresh Flow
```
1. Access token hết hạn
   - Client nhận 401 response
   
2. Client gửi refresh token
   POST /back-office/auth/refresh
   { "refresh": "eyJ0eXAi..." }
   
3. Server validate refresh token
   - Check signature
   - Check expiration
   - Check blacklist (nếu có)
   
4. Server tạo tokens mới
   {
     "access": "new_access_token",
     "refresh": "new_refresh_token"
   }
   
5. Client update tokens
   - Lưu tokens mới
   - Retry original request
```

### App Authentication

**Similar to Web but với AppUser**:
```python
# app_user_id từ Firebase Auth hoặc third-party
POST /app/auth/login
{
  "app_user_id": "firebase_uid",
  "name": "User Name",
  "avatar_url": "https://..."
}

Response:
{
  "access": "...",
  "refresh": "...",
  "app_user": { ... }
}
```

---

## FILE STORAGE

### Storage Backends

#### 1. Google Drive Storage
**Use cases**: 
- Lesson documentation (PDF, slides)
- Student avatars
- Facility images

**Implementation**:
```python
from steam_api.helpers.google_drive_storage import GoogleDriveStorage

storage = GoogleDriveStorage()

# Upload file
file_url = storage.upload_file(
    file=file_object,
    filename="document.pdf",
    folder_id=settings.GDRIVE_DEFAULT_FOLDER_ID
)

# Get public link
public_url = storage.get_public_url(file_id)
```

**Configuration**:
```python
# Service account authentication
GDRIVE_SERVICE_ACCOUNT_FILE = "service_account.json"
GDRIVE_DEFAULT_FOLDER_ID = "folder_id"
```

#### 2. Local Storage
**Use cases**: 
- Development/testing
- Temporary files
- Media files

**Configuration**:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### File Upload Flow

```
1. Client upload file
   POST /back-office/lesson-documentations
   Content-Type: multipart/form-data
   
2. Server receives file
   - Validate file type
   - Validate file size
   - Generate unique filename
   
3. Upload to storage
   - Google Drive hoặc Local
   - Get public URL
   
4. Save URL to database
   LessonDocumentation.objects.create(
       lesson=lesson,
       file_url=file_url,
       file_name=filename
   )
   
5. Response với URL
   {
     "id": 1,
     "file_url": "https://drive.google.com/...",
     "file_name": "document.pdf"
   }
```

---

## CACHING STRATEGY

### Cache Layers

#### 1. OTP Cache (Redis)
```python
from django.core.cache import cache

# Store OTP
cache.set(f'otp:{email}', otp_code, timeout=300)  # 5 minutes

# Verify OTP
stored_otp = cache.get(f'otp:{email}')
if stored_otp == provided_otp:
    cache.delete(f'otp:{email}')
    return True
```

#### 2. Session Cache
```python
# Django session stored in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### 3. Query Result Cache
```python
from django.core.cache import cache

def get_active_courses():
    cache_key = 'active_courses'
    courses = cache.get(cache_key)
    
    if courses is None:
        courses = Course.objects.filter(
            is_active=True,
            deleted_at__isnull=True
        )
        cache.set(cache_key, courses, timeout=3600)  # 1 hour
    
    return courses
```

#### 4. View Cache
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache 15 minutes
def course_list_view(request):
    ...
```

### Cache Invalidation

**Strategies**:
1. **Time-based**: Cache tự động expire sau X seconds
2. **Event-based**: Clear cache khi data thay đổi

```python
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

@receiver(post_save, sender=Course)
def invalidate_course_cache(sender, instance, **kwargs):
    cache.delete('active_courses')
    cache.delete(f'course_{instance.id}')
```

---

## LOGGING & MONITORING

### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'logtail': {
            'class': 'logtail.LogtailHandler',
            'source_token': settings.BETTERSTACK_LOG_TOKEN,
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['logtail', 'console'],
            'level': 'INFO',
        },
    },
}
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# Info logs
logger.info('User logged in', extra={
    'user_id': user.id,
    'email': user.email
})

# Warning logs
logger.warning('Invalid login attempt', extra={
    'email': email,
    'ip': request.META.get('REMOTE_ADDR')
})

# Error logs
try:
    ...
except Exception as e:
    logger.error('Error processing payment', extra={
        'student_id': student.id,
        'amount': amount
    }, exc_info=True)
```

### Monitoring Metrics

**Key Metrics to Monitor**:
1. **API Response Time**: Track slow endpoints
2. **Error Rate**: Monitor 500 errors
3. **Database Query Time**: Identify slow queries
4. **Cache Hit Rate**: Optimize caching
5. **Active Users**: Track concurrent users
6. **File Upload Success Rate**: Storage reliability

### Health Check Endpoint

```python
# steam_api/views/health.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

class HealthCheckView(APIView):
    def get(self, request):
        # Check database
        try:
            connection.ensure_connection()
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"
        
        # Check Redis
        try:
            cache.set('health_check', 'ok', 10)
            cache_status = "healthy"
        except Exception:
            cache_status = "unhealthy"
        
        return Response({
            'status': 'ok',
            'database': db_status,
            'cache': cache_status
        })
```

**Usage**:
```bash
curl http://localhost:8000/health/
```

---

## SECURITY CONSIDERATIONS

### 1. Authentication & Authorization
- JWT tokens với expiration
- Password hashing (bcrypt)
- Role-based access control
- Token refresh mechanism

### 2. Input Validation
- Serializer validation
- Model validation
- SQL injection prevention (ORM)
- XSS prevention (DRF auto-escaping)

### 3. CORS Configuration
```python
CORS_ALLOW_ALL_ORIGINS = False  # Don't use in production
CORS_ALLOWED_ORIGINS = [
    "https://admin.bdu.edu.vn",
    "https://app.bdu.edu.vn"
]
```

### 4. HTTPS/SSL
- Use HTTPS in production
- Secure cookie flags
- HSTS headers

### 5. Rate Limiting
```python
# TODO: Implement rate limiting
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## DEPLOYMENT ARCHITECTURE

### Production Setup

```
                    ┌─────────────┐
                    │   Nginx     │
                    │ (Web Server)│
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌──────▼──────┐
         │  Gunicorn   │      │   Static    │
         │  (WSGI)     │      │   Files     │
         └──────┬──────┘      └─────────────┘
                │
         ┌──────▼──────┐
         │   Django    │
         │ Application │
         └──────┬──────┘
                │
        ┌───────┴───────┐
        │               │
  ┌─────▼─────┐   ┌────▼────┐
  │   MySQL   │   │  Redis  │
  │ (Database)│   │ (Cache) │
  └───────────┘   └─────────┘
```

### Scalability Options

**Vertical Scaling**: Upgrade server resources
**Horizontal Scaling**: 
- Multiple Gunicorn workers
- Load balancer (Nginx)
- Database replication (Master-Slave)
- Redis Sentinel for HA

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-30

