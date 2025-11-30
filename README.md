# HỆ THỐNG QUẢN LÝ KHÓA HỌC STEAM - BDU

## MỤC LỤC
1. [Tổng quan hệ thống](#tổng-quan-hệ-thống)
2. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
3. [Công nghệ sử dụng](#công-nghệ-sử-dụng)
4. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
5. [Mô hình dữ liệu](#mô-hình-dữ-liệu)
6. [Hướng dẫn cài đặt](#hướng-dẫn-cài-đặt)
7. [Hướng dẫn chạy dự án](#hướng-dẫn-chạy-dự-án)
8. [Tài liệu API](#tài-liệu-api)
9. [Giải thích nghiệp vụ](#giải-thích-nghiệp-vụ)
10. [Quy trình làm việc](#quy-trình-làm-việc)

---

## TỔNG QUAN HỆ THỐNG

### Giới thiệu
Hệ thống quản lý khóa học STEAM (Science, Technology, Engineering, Arts, Mathematics) cho Trường Đại học Bình Dương (BDU). Đây là một nền tảng quản lý toàn diện giúp tổ chức các khóa học, lớp học, điểm danh, đánh giá học viên và quản lý cơ sở vật chất.

### Mục đích
- **Quản lý khóa học**: Tạo và quản lý các khóa học STEAM với thông tin chi tiết
- **Quản lý lớp học**: Tổ chức lớp học, phân công giáo viên, trợ giảng
- **Quản lý học viên**: Đăng ký học viên, theo dõi thông tin và tiến độ học tập
- **Điểm danh**: Hệ thống điểm danh tự động và thủ công
- **Đánh giá**: Đánh giá chi tiết học viên qua 12 tiêu chí
- **Quản lý cơ sở vật chất**: Quản lý thông tin về cơ sở vật chất, phòng học
- **Quản lý tài chính**: Theo dõi học phí, thanh toán

### Người dùng hệ thống
1. **Root**: Quản trị viên cao nhất, có toàn quyền quản lý hệ thống
2. **Manager**: Quản lý viên, quản lý khóa học, lớp học, học viên
3. **Teacher**: Giáo viên, giảng dạy và đánh giá học viên
4. **Teaching Assistant**: Trợ giảng, hỗ trợ giảng dạy
5. **Parent/Guardian**: Phụ huynh, xem thông tin học tập của con em (qua App)

---

## KIẾN TRÚC HỆ THỐNG

### Kiến trúc tổng quan
Hệ thống được xây dựng theo mô hình **Monolithic Architecture** với Django REST Framework.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │   Web Portal    │              │  Mobile App     │           │
│  │  (Back Office)  │              │  (Parent/GV)    │           │
│  └─────────────────┘              └─────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                              │
│                    Django REST Framework                         │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ /back-office/*   │         │    /app/*        │             │
│  │ (Web Admin APIs) │         │  (Mobile APIs)   │             │
│  └──────────────────┘         └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  ViewSets    │  │ Serializers  │  │ Middlewares  │         │
│  │              │  │              │  │              │         │
│  │ - Web Views  │  │ - Validation │  │ - Auth JWT   │         │
│  │ - App Views  │  │ - Transform  │  │ - Permission │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                          │
│                      Django ORM Models                           │
│  ┌──────────────────────────────────────────────────┐           │
│  │ Student │ Course │ ClassRoom │ Lesson │ etc...   │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐              │
│  │   MySQL    │  │   Redis    │  │Google Drive │              │
│  │ (Database) │  │  (Cache)   │  │  (Storage)  │              │
│  └────────────┘  └────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Các thành phần chính

#### 1. API Layer
- **Web APIs** (`/back-office/*`): APIs cho quản trị viên, giáo viên
- **App APIs** (`/app/*`): APIs cho ứng dụng mobile (phụ huynh, giáo viên)
- **Health Check** (`/health/`): Kiểm tra sức khỏe hệ thống

#### 2. Authentication & Authorization
- **JWT Token**: Sử dụng Simple JWT cho xác thực
- **Custom User Model**: `WebUser` cho web, `AppUser` cho mobile
- **Role-Based Access Control**: Root, Manager, Teacher
- **Middleware**: Custom authentication rules

#### 3. Database
- **Primary Database**: MySQL 8.0
- **Cache**: Redis 6.0
- **ORM**: Django ORM
- **Migrations**: Django migrations

#### 4. External Services
- **Google Drive API**: Lưu trữ file, hình ảnh
- **Email Service**: SMTP Gmail cho gửi OTP, thông báo
- **BetterStack Logging**: Logging tập trung

---

## CÔNG NGHỆ SỬ DỤNG

### Backend Framework
- **Django 5.2.8**: Web framework chính
- **Django REST Framework 3.16.1**: Xây dựng RESTful APIs
- **drf-yasg 1.21.11**: Tự động tạo Swagger documentation

### Database & Caching
- **PyMySQL 1.1.2**: MySQL database connector
- **Django Redis 6.0**: Redis cache backend
- **Redis 6.0**: In-memory caching

### Authentication & Security
- **djangorestframework-simplejwt 5.5.1**: JWT authentication
- **PyJWT 2.10.1**: JWT token handling
- **bcrypt 5.0.0**: Password hashing

### File Storage
- **Pillow 12.0.0**: Image processing
- **firebase_admin 7.1.0**: Firebase integration
- **google-api-python-client 2.187.0**: Google Drive API
- **google-auth**: Google authentication

### Utilities
- **python-decouple 3.8**: Environment variable management
- **django-cors-headers 4.9.0**: CORS handling
- **whitenoise 6.11.0**: Static file serving
- **gunicorn 23.0.0**: WSGI HTTP server
- **requests 2.32.5**: HTTP client
- **logtail-python 0.3.4**: Logging service

### Development Tools
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

---

## CẤU TRÚC THƯ MỤC

```
bdu_steam/
│
├── steam/                          # Django project settings
│   ├── __init__.py                 # PyMySQL configuration
│   ├── settings.py                 # Project settings
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py                     # WSGI application
│   └── asgi.py                     # ASGI application
│
├── steam_api/                      # Main Django app
│   │
│   ├── models/                     # Data models
│   │   ├── web_user.py            # Web user (admin, teacher)
│   │   ├── app_user.py            # Mobile app user
│   │   ├── student.py             # Student information
│   │   ├── course.py              # Course information
│   │   ├── class_room.py          # Class management
│   │   ├── course_module.py       # Course modules
│   │   ├── lesson.py              # Lesson management
│   │   ├── attendance.py          # Attendance tracking
│   │   ├── lesson_evaluation.py   # Student evaluation
│   │   ├── course_registration.py # Course registration
│   │   ├── facility.py            # Facility management
│   │   ├── news.py                # News/announcements
│   │   └── ...
│   │
│   ├── serializers/                # API serializers
│   │   ├── custom_token_*.py      # JWT token serializers
│   │   ├── student.py             # Student serializer
│   │   ├── course.py              # Course serializer
│   │   └── ...
│   │
│   ├── views/                      # API views
│   │   ├── web/                   # Back-office APIs
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── student.py        # Student management
│   │   │   ├── course.py         # Course management
│   │   │   ├── class_room.py     # Class management
│   │   │   ├── lesson.py         # Lesson management
│   │   │   ├── attendance.py     # Attendance management
│   │   │   └── ...
│   │   │
│   │   └── app/                   # Mobile app APIs
│   │       ├── auth.py           # App authentication
│   │       ├── course.py         # View courses
│   │       ├── lesson.py         # View lessons
│   │       ├── attendance.py     # Attendance check-in
│   │       └── ...
│   │
│   ├── middlewares/                # Custom middlewares
│   │   ├── app_authentication.py  # App auth middleware
│   │   ├── web_authentication.py  # Web auth middleware
│   │   ├── permissions.py         # Permission checks
│   │   └── custom_user_authentication_rule.py
│   │
│   ├── helpers/                    # Helper functions
│   │   ├── firebase_storage.py    # Firebase storage
│   │   ├── google_drive_storage.py # Google Drive storage
│   │   ├── local_storage.py       # Local file storage
│   │   ├── lesson_schedule.py     # Lesson scheduling logic
│   │   ├── otp.py                 # OTP generation
│   │   ├── response.py            # API response helpers
│   │   └── send_html_email.py     # Email sending
│   │
│   ├── const/                      # Constants
│   │   ├── const.py               # General constants
│   │   └── score_criteria.py      # Evaluation criteria
│   │
│   ├── templates/                  # Email templates
│   │   ├── otp.html              # OTP email template
│   │   └── password_reset.html   # Password reset template
│   │
│   └── urls.py                     # App URL configuration
│
├── venv/                           # Python virtual environment
├── media/                          # Media files (images, documents)
├── static/                         # Static files (CSS, JS)
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image configuration
├── docker-compose.yaml             # Docker Compose configuration
├── service_account.json.gpg        # Google service account (encrypted)
└── README.md                       # Project documentation
```

---

## MÔ HÌNH DỮ LIỆU

### ERD (Entity Relationship Diagram)

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   WebUser    │         │   Course     │         │   Student    │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │         │ id (PK)      │         │ id (PK)      │
│ staff_id     │         │ name         │         │ identification│
│ email        │◄────┐   │ description  │         │ first_name   │
│ name         │     │   │ thumbnail    │         │ last_name    │
│ role         │     │   │ price        │         │ date_of_birth│
│ status       │     │   │ duration     │         │ parent_name  │
└──────────────┘     │   └──────────────┘         │ parent_phone │
                     │          │                  └──────────────┘
                     │          │ 1                       │
                     │          │                         │ N
                     │          ▼ N                       │
                     │   ┌──────────────┐                 │
                     └───┤  ClassRoom   │                 │
                    1    ├──────────────┤                 │
              teacher/TA │ id (PK)      │                 │
                         │ name         │                 │
                         │ course_id(FK)│                 │
                         │ teacher(FK)  │                 │
                         │ TA(FK)       │                 │
                         │ start_date   │                 │
                         │ end_date     │                 │
                         │ schedule(JSON)│                │
                         └──────────────┘                 │
                                │                         │
                                │ 1                       │
                                │                         │
                                ▼ N                       │
                         ┌──────────────┐                 │
                         │CourseModule  │                 │
                         ├──────────────┤                 │
                         │ id (PK)      │                 │
                         │ class_id(FK) │                 │
                         │ name         │                 │
                         │ description  │                 │
                         │ sequence_no  │                 │
                         │ total_lessons│                 │
                         └──────────────┘                 │
                                │                         │
                                │ 1                       │
                                │                         │
                                ▼ N                       │
                         ┌──────────────┐         N       │
                         │   Lesson     │◄────────────────┤
                         ├──────────────┤                 │
                         │ id (PK)      │                 │
                         │ module_id(FK)│         ┌───────┴──────┐
                         │ name         │         │Course        │
                         │ sequence_no  │         │Registration  │
                         └──────────────┘         ├──────────────┤
                                │                 │ id (PK)      │
                                │                 │ student(FK)  │
                           1    │    N            │ class_room   │
                                ├─────────────┐   │ status       │
                                │             │   │ amount       │
                                ▼             ▼   │ paid_amount  │
                         ┌──────────────┐ ┌──────────────┐      │
                         │ Attendance   │ │Lesson        │      │
                         ├──────────────┤ │Evaluation    │      │
                         │ id (PK)      │ ├──────────────┤      │
                         │ student(FK)  │ │ id (PK)      │      │
                         │ lesson(FK)   │ │ lesson(FK)   │      │
                         │ status       │ │ student(FK)  │      │
                         │ check_in_time│ │ focus_score  │      │
                         │ note         │ │ punctuality  │      │
                         └──────────────┘ │ interaction  │      │
                                          │ ...12 scores │      │
                         ┌──────────────┐ │ comment      │      │
                         │ Facility     │ └──────────────┘      │
                         ├──────────────┤                       │
                         │ id (PK)      │                       │
                         │ name         │                       │
                         │ description  │                       │
                         └──────────────┘                       │
                                │                               │
                                │ 1                             │
                                │                               │
                                ▼ N                             │
                         ┌──────────────┐                       │
                         │FacilityImage │                       │
                         ├──────────────┤                       │
                         │ id (PK)      │                       │
                         │ facility(FK) │                       │
                         │ image_url    │                       │
                         └──────────────┘                       │
                                                                │
                         ┌──────────────┐                       │
                         │    News      │                       │
                         ├──────────────┤                       │
                         │ id (PK)      │                       │
                         │ title        │                       │
                         │ link         │                       │
                         │ image        │                       │
                         │ posted_at    │                       │
                         └──────────────┘                       │
```

### Các bảng chính

#### 1. WebUser - Người dùng hệ thống Web
```python
- id: ID người dùng
- staff_id: Mã nhân viên (unique)
- name: Họ tên
- email: Email (unique, username)
- birth_date: Ngày sinh
- gender: Giới tính (male/female/other)
- phone: Số điện thoại
- status: Trạng thái (blocked/activated/unverified)
- role: Vai trò (root/manager/teacher)
```

#### 2. Student - Học viên
```python
- id: ID học viên
- identification_number: Số giấy khai sinh/CMND (unique)
- first_name, last_name: Họ và tên
- date_of_birth: Ngày sinh
- gender: Giới tính
- address: Địa chỉ
- phone_number, email: Liên hệ
- parent_name, parent_phone, parent_email: Thông tin phụ huynh
- avatar_url: Ảnh đại diện
- is_active: Trạng thái hoạt động
```

#### 3. Course - Khóa học
```python
- id: ID khóa học
- name: Tên khóa học
- description: Mô tả
- thumbnail_url: Ảnh thumbnail
- price: Học phí
- duration: Thời lượng (phút)
- is_active: Trạng thái
```

#### 4. ClassRoom - Lớp học
```python
- id: ID lớp học
- name: Tên lớp
- course: Khóa học (FK)
- teacher: Giáo viên chính (FK to WebUser)
- teaching_assistant: Trợ giảng (FK to WebUser)
- max_students: Số lượng học viên tối đa
- start_date, end_date: Ngày bắt đầu/kết thúc
- schedule: Lịch học (JSON format)
```

**Schedule JSON format**:
```json
{
  "monday": [
    {"start_time": "08:00", "end_time": "10:00"}
  ],
  "wednesday": [
    {"start_time": "14:00", "end_time": "16:00"}
  ]
}
```

#### 5. CourseModule - Module khóa học
```python
- id: ID module
- class_room: Lớp học (FK)
- name: Tên module
- description: Mô tả
- sequence_number: Thứ tự module
- total_lessons: Tổng số buổi học
```

#### 6. Lesson - Buổi học
```python
- id: ID buổi học
- module: Module (FK)
- name: Tên buổi học
- sequence_number: Thứ tự buổi học trong module
```

**Properties (computed)**:
- `status`: Trạng thái buổi học (not_started/in_progress/completed)
- `start_datetime`: Thời gian bắt đầu (tự động tính)
- `end_datetime`: Thời gian kết thúc (tự động tính)

#### 7. Attendance - Điểm danh
```python
- id: ID điểm danh
- student: Học viên (FK)
- lesson: Buổi học (FK)
- status: Trạng thái (present/absent/late/excused)
- check_in_time: Thời gian check-in
- note: Ghi chú
```

#### 8. LessonEvaluation - Đánh giá buổi học
```python
- id: ID đánh giá
- lesson: Buổi học (FK)
- student: Học viên (FK)
- focus_score: Điểm tập trung (1-5)
- punctuality_score: Điểm đúng giờ (1-5)
- interaction_score: Điểm tương tác (1-5)
- project_idea_score: Điểm ý tưởng dự án (1-5)
- critical_thinking_score: Điểm tư duy phản biện (1-5)
- teamwork_score: Điểm làm việc nhóm (1-5)
- idea_sharing_score: Điểm chia sẻ ý tưởng (1-5)
- creativity_score: Điểm sáng tạo (1-5)
- communication_score: Điểm giao tiếp (1-5)
- homework_score: Điểm bài tập (1-5)
- old_knowledge_score: Điểm kiến thức cũ (1-5)
- new_knowledge_score: Điểm kiến thức mới (1-5)
- comment: Nhận xét của giáo viên
```

#### 9. CourseRegistration - Đăng ký khóa học
```python
- id: ID đăng ký
- student: Học viên (FK)
- class_room: Lớp học (FK)
- status: Trạng thái (pending/approved/rejected/cancelled)
- amount: Số tiền phải trả
- paid_amount: Số tiền đã trả
- payment_status: Trạng thái thanh toán (unpaid/partially_paid/fully_paid)
- payment_method: Phương thức thanh toán
- contact_for_anonymous: Thông tin liên hệ (JSON)
- note: Ghi chú
```

#### 10. Facility - Cơ sở vật chất
```python
- id: ID cơ sở
- name: Tên cơ sở
- description: Mô tả
```

---

## HƯỚNG DẪN CÀI ĐẶT

### Yêu cầu hệ thống
- Python 3.11+
- MySQL 8.0+
- Redis 6.0+
- Docker & Docker Compose (optional)

### Cài đặt Local (không dùng Docker)

#### Bước 1: Clone repository
```bash
git clone <repository-url>
cd bdu_steam
```

#### Bước 2: Tạo virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows
```

#### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

**Lưu ý trên macOS**: Nếu gặp lỗi khi cài `mysqlclient`, hệ thống đã được cấu hình sử dụng `PyMySQL` thay thế.

#### Bước 4: Cài đặt MySQL
```bash
# macOS với Homebrew
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt-get install mysql-server
sudo systemctl start mysql

# Tạo database
mysql -u root -p
CREATE DATABASE steam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'steam_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON steam.* TO 'steam_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Bước 5: Cài đặt Redis
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

#### Bước 6: Cấu hình biến môi trường
Tạo file `.env` trong thư mục root:
```bash
# Database
DATABASE_ENGINE=mysql
DATABASE_NAME=steam
DATABASE_USER=steam_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=
REDIS_PASSWORD=

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging (BetterStack)
BETTERSTACK_LOG_TOKEN=your-token
BETTERSTACK_LOG_HOST=your-host

# Google Drive
GDRIVE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json
GDRIVE_DEFAULT_FOLDER_ID=your-folder-id
```

#### Bước 7: Setup Google Drive API (optional)
1. Tạo project trên Google Cloud Console
2. Bật Google Drive API
3. Tạo Service Account
4. Tải service account JSON key
5. Giải mã `service_account.json.gpg` hoặc sử dụng file mới

```bash
# Nếu có file .gpg
gpg --decrypt service_account.json.gpg > service_account.json
```

#### Bước 8: Chạy migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Bước 9: Tạo superuser
```bash
python manage.py createsuperuser
```

#### Bước 10: Chạy development server
```bash
python manage.py runserver
```

Server sẽ chạy tại: `http://localhost:8000`

---

## HƯỚNG DẪN CHẠY DỰ ÁN

### Chạy với Docker Compose (Khuyến nghị)

#### Bước 1: Chuẩn bị file cấu hình
Chỉnh sửa `docker-compose.yaml`:
```yaml
services:
  steam_backend:
    ports:
      - "8000:8000"  # Đổi port nếu cần
    volumes:
      - /path/to/service_account.json:/usr/src/app/service_account.json
    environment:
      - DATABASE_ENGINE=mysql
      - DATABASE_NAME=steam
      - DATABASE_USER=root
      - DATABASE_PASSWORD=steam
      - DATABASE_HOST=steam_mysql
      - DATABASE_PORT=3306
      # ... các biến môi trường khác

  steam_mysql:
    ports:
      - "3307:3306"  # Đổi port host nếu cần
    volumes:
      - ./mysql_data:/var/lib/mysql

  steam_redis:
    ports:
      - "6380:6379"  # Đổi port host nếu cần
```

#### Bước 2: Build và chạy
```bash
# Build images
docker-compose build

# Chạy containers
docker-compose up -d

# Xem logs
docker-compose logs -f steam_backend
```

#### Bước 3: Setup database (lần đầu tiên)
```bash
# Chạy migrations
docker-compose exec steam_backend python manage.py migrate

# Tạo superuser
docker-compose exec steam_backend python manage.py createsuperuser
```

#### Các lệnh quản lý Docker
```bash
# Dừng containers
docker-compose stop

# Khởi động lại
docker-compose restart

# Xóa containers
docker-compose down

# Xóa containers và volumes
docker-compose down -v

# Xem logs
docker-compose logs -f [service_name]

# Vào container
docker-compose exec steam_backend bash
```

### Chạy development server (Local)

```bash
# Kích hoạt virtual environment
source venv/bin/activate

# Chạy server
python manage.py runserver

# Chạy với custom port
python manage.py runserver 0.0.0.0:8080

# Chạy migrations
python manage.py makemigrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

### Chạy production server

```bash
# Sử dụng Gunicorn
gunicorn steam.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Với logging
gunicorn steam.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

---

## TÀI LIỆU API

### API Documentation
Swagger UI tự động được tạo bởi `drf-yasg`.

**URL**: `http://localhost:8000/swagger/` hoặc `http://localhost:8000/redoc/`

### Authentication
Hệ thống sử dụng JWT (JSON Web Token) cho authentication.

#### Lấy Access Token (Web)
```http
POST /back-office/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "role": "teacher"
  }
}
```

#### Refresh Token
```http
POST /back-office/auth/refresh
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Sử dụng Token trong API calls
```http
GET /back-office/students
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Các API Endpoints chính

#### Back-Office APIs (`/back-office/`)

**Authentication**
- `POST /back-office/auth/login` - Đăng nhập
- `POST /back-office/auth/refresh` - Refresh token
- `POST /back-office/auth/logout` - Đăng xuất
- `POST /back-office/auth/register` - Đăng ký (root only)
- `POST /back-office/auth/forgot-password` - Quên mật khẩu
- `POST /back-office/auth/reset-password` - Đặt lại mật khẩu

**Users Management**
- `GET /back-office/users` - Danh sách users
- `POST /back-office/users` - Tạo user mới
- `GET /back-office/users/{id}` - Chi tiết user
- `PUT /back-office/users/{id}` - Cập nhật user
- `DELETE /back-office/users/{id}` - Xóa user

**Students Management**
- `GET /back-office/students` - Danh sách học viên
- `POST /back-office/students` - Tạo học viên mới
- `GET /back-office/students/{id}` - Chi tiết học viên
- `PUT /back-office/students/{id}` - Cập nhật học viên
- `DELETE /back-office/students/{id}` - Xóa học viên

**Courses Management**
- `GET /back-office/courses` - Danh sách khóa học
- `POST /back-office/courses` - Tạo khóa học
- `GET /back-office/courses/{id}` - Chi tiết khóa học
- `PUT /back-office/courses/{id}` - Cập nhật khóa học
- `DELETE /back-office/courses/{id}` - Xóa khóa học

**Classes Management**
- `GET /back-office/classes` - Danh sách lớp học
- `POST /back-office/classes` - Tạo lớp học
- `GET /back-office/classes/{id}` - Chi tiết lớp học
- `PUT /back-office/classes/{id}` - Cập nhật lớp học
- `DELETE /back-office/classes/{id}` - Xóa lớp học

**Lessons Management**
- `GET /back-office/lessons` - Danh sách buổi học
- `POST /back-office/lessons` - Tạo buổi học
- `GET /back-office/lessons/{id}` - Chi tiết buổi học
- `PUT /back-office/lessons/{id}` - Cập nhật buổi học
- `DELETE /back-office/lessons/{id}` - Xóa buổi học

**Attendance Management**
- `GET /back-office/attendances` - Danh sách điểm danh
- `POST /back-office/attendances` - Tạo điểm danh
- `PUT /back-office/attendances/{id}` - Cập nhật điểm danh
- `POST /back-office/lesson-checkins` - Check-in cho buổi học

**Evaluation Management**
- `GET /back-office/lesson-evaluations` - Danh sách đánh giá
- `POST /back-office/lesson-evaluations` - Tạo đánh giá
- `PUT /back-office/lesson-evaluations/{id}` - Cập nhật đánh giá
- `GET /back-office/evaluation-criteria` - Tiêu chí đánh giá

**Facilities Management**
- `GET /back-office/facilities` - Danh sách cơ sở vật chất
- `POST /back-office/facilities` - Tạo cơ sở mới
- `PUT /back-office/facilities/{id}` - Cập nhật cơ sở
- `DELETE /back-office/facilities/{id}` - Xóa cơ sở

**News Management**
- `GET /back-office/news` - Danh sách tin tức
- `POST /back-office/news` - Tạo tin tức
- `PUT /back-office/news/{id}` - Cập nhật tin tức
- `DELETE /back-office/news/{id}` - Xóa tin tức

#### Mobile App APIs (`/app/`)

**Authentication**
- `POST /app/auth/login` - Đăng nhập app
- `POST /app/auth/refresh` - Refresh token

**Courses & Classes**
- `GET /app/courses` - Danh sách khóa học
- `GET /app/classes` - Danh sách lớp học

**Lessons**
- `GET /app/lessons` - Danh sách buổi học
- `GET /app/lessons/{id}` - Chi tiết buổi học

**Attendance**
- `GET /app/attendances` - Lịch sử điểm danh
- `POST /app/attendances/check-in` - Check-in

**Evaluations**
- `GET /app/lesson-evaluations` - Xem đánh giá học viên

**Timetable**
- `GET /app/time-tables` - Lịch học

**News**
- `GET /app/news` - Tin tức

**Facilities**
- `GET /app/facilities` - Xem cơ sở vật chất

---

## GIẢI THÍCH NGHIỆP VỤ

### 1. Quản lý Khóa học và Lớp học

#### Quy trình tạo lớp học
1. **Tạo Course (Khóa học)**: 
   - Admin/Manager tạo khóa học với thông tin: tên, mô tả, giá, thời lượng
   - Khóa học là template, có thể tạo nhiều lớp từ 1 khóa học

2. **Tạo ClassRoom (Lớp học)**:
   - Chọn khóa học
   - Phân công giáo viên, trợ giảng
   - Thiết lập thời gian: ngày bắt đầu, ngày kết thúc
   - Thiết lập lịch học (schedule JSON)
   - Số lượng học viên tối đa

3. **Tạo CourseModule (Module)**:
   - Mỗi lớp học có nhiều module
   - Module có thứ tự (sequence_number)
   - Mỗi module có số buổi học nhất định

4. **Tạo Lesson (Buổi học)**:
   - Mỗi module có nhiều buổi học
   - Buổi học có thứ tự trong module
   - Thời gian buổi học được tính tự động dựa trên schedule của lớp

#### Tính toán lịch học tự động
Hệ thống tự động tính toán thời gian các buổi học dựa trên:
- Ngày bắt đầu lớp
- Lịch học trong tuần (schedule JSON)
- Thứ tự buổi học (sequence_number)

**Ví dụ**:
```
Lớp học:
- Bắt đầu: 01/01/2025
- Lịch: Thứ 2, 4, 6 (8:00-10:00)

Module 1: 6 buổi
  → Lesson 1: 01/01/2025 (T2) 8:00-10:00
  → Lesson 2: 03/01/2025 (T4) 8:00-10:00
  → Lesson 3: 05/01/2025 (T6) 8:00-10:00
  → ...
```

### 2. Quản lý Học viên

#### Quy trình đăng ký học
1. **Tạo Student (Học viên)**:
   - Thông tin cá nhân: họ tên, ngày sinh, giới tính
   - Số giấy khai sinh/CMND (unique identifier)
   - Thông tin phụ huynh: tên, số điện thoại, email

2. **Course Registration (Đăng ký lớp)**:
   - Chọn học viên và lớp học
   - Nhập thông tin học phí: amount
   - Trạng thái mặc định: approved
   - Trạng thái thanh toán: unpaid

3. **Kiểm tra điều kiện**:
   - Lớp học chưa đầy (current_students < max_students)
   - Học viên chưa đăng ký lớp này
   - Lớp học còn active

#### Quản lý học phí
- `amount`: Tổng học phí phải trả
- `paid_amount`: Số tiền đã trả
- `payment_status`: Tự động cập nhật
  - `unpaid`: paid_amount = 0
  - `partially_paid`: 0 < paid_amount < amount
  - `fully_paid`: paid_amount >= amount

### 3. Điểm danh (Attendance)

#### Các trạng thái điểm danh
- `present`: Có mặt
- `absent`: Vắng mặt
- `late`: Đi muộn
- `excused`: Có phép

#### Quy trình điểm danh

**Cách 1: Check-in tự động (Mobile App)**
```
1. Học viên/Phụ huynh mở app
2. Chọn buổi học đang diễn ra
3. Check-in
4. Hệ thống tự động:
   - Tạo Attendance record
   - Đánh dấu status = "present"
   - Lưu check_in_time = hiện tại
```

**Cách 2: Giáo viên điểm danh thủ công (Web)**
```
1. Giáo viên vào buổi học
2. Xem danh sách học viên trong lớp
3. Đánh dấu từng học viên:
   - Present, Absent, Late, Excused
4. Thêm ghi chú nếu cần
```

**Cách 3: Điểm danh hàng loạt (Lesson Check-in)**
```
POST /back-office/lesson-checkins
{
  "lesson_id": 123,
  "attendances": [
    {"student_id": 1, "status": "present"},
    {"student_id": 2, "status": "late"},
    {"student_id": 3, "status": "absent"}
  ]
}
```

### 4. Đánh giá Học viên (Lesson Evaluation)

#### 12 tiêu chí đánh giá (thang điểm 1-5)

1. **Focus Score (Mức độ tập trung)**
   - 1: Không tập trung
   - 5: Hoàn toàn tập trung

2. **Punctuality Score (Đúng giờ)**
   - 1: Thường xuyên đi muộn/về sớm
   - 5: Luôn đúng giờ

3. **Interaction Score (Mức độ tương tác)**
   - 1: Thụ động
   - 5: Tương tác xuất sắc

4. **Project Idea Score (Ý tưởng dự án)**
   - 1: Không có ý tưởng
   - 5: Ý tưởng xuất sắc

5. **Critical Thinking Score (Tư duy phản biện)**
   - 1: Không có tư duy phản biện
   - 5: Tư duy phản biện xuất sắc

6. **Teamwork Score (Hợp tác nhóm)**
   - 1: Không hợp tác
   - 5: Hợp tác xuất sắc

7. **Idea Sharing Score (Chia sẻ ý tưởng)**
   - 1: Không chia sẻ
   - 5: Chia sẻ xuất sắc

8. **Creativity Score (Sáng tạo)**
   - 1: Không sáng tạo
   - 5: Sáng tạo xuất sắc

9. **Communication Score (Giao tiếp)**
   - 1: Kém hiệu quả
   - 5: Xuất sắc

10. **Homework Score (Bài tập về nhà)**
    - 1: Không hoàn thành
    - 5: Hoàn thành xuất sắc

11. **Old Knowledge Score (Kiến thức cũ)**
    - 1: Không nắm vững
    - 5: Nắm vững xuất sắc

12. **New Knowledge Score (Kiến thức mới)**
    - 1: Khó tiếp thu
    - 5: Tiếp thu xuất sắc

#### Quy trình đánh giá
```
1. Sau mỗi buổi học
2. Giáo viên đánh giá từng học viên
3. Chấm điểm 12 tiêu chí
4. Viết nhận xét (comment)
5. Lưu đánh giá
```

#### Xem đánh giá
- Giáo viên: Xem và chỉnh sửa đánh giá của mình
- Phụ huynh: Xem đánh giá của con em (qua App)
- Manager: Xem tất cả đánh giá

### 5. Quản lý Tài liệu & Media

#### Lesson Documentation
- Tài liệu buổi học: slides, bài tập, tài liệu tham khảo
- Upload file lên Google Drive
- Lưu URL trong database

#### Lesson Gallery
- Ảnh hoạt động trong buổi học
- Upload qua API
- Lưu trữ trên Google Drive hoặc local storage
- Hiển thị gallery cho từng buổi học

### 6. Quản lý Cơ sở vật chất

#### Facility
- Thông tin về phòng học, thiết bị
- Mô tả chi tiết
- Album hình ảnh (FacilityImage)

#### Quy trình quản lý
```
1. Tạo Facility (cơ sở)
2. Upload hình ảnh (FacilityImage)
3. Hiển thị trên App cho phụ huynh xem
4. Cập nhật/xóa khi cần
```

### 7. Tin tức & Thông báo (News)

#### Chức năng
- Đăng tin tức, thông báo
- Hiển thị trên App
- Link đến bài viết đầy đủ
- Hình ảnh thumbnail

#### Quy trình
```
1. Admin tạo News
2. Nhập: tiêu đề, link, hình ảnh, thời gian đăng
3. App users xem danh sách news
4. Click vào để xem chi tiết
```

---

## QUY TRÌNH LÀM VIỆC

### 1. Quy trình bắt đầu khóa học mới

```
1. Manager tạo Course
   ↓
2. Manager tạo ClassRoom từ Course
   - Chọn giáo viên
   - Thiết lập lịch học
   ↓
3. Manager tạo CourseModule cho ClassRoom
   - Module 1: Làm quen (4 buổi)
   - Module 2: Cơ bản (6 buổi)
   - ...
   ↓
4. Hệ thống tự động tạo Lesson cho mỗi Module
   ↓
5. Manager/Staff đăng ký học viên
   - Tạo Student
   - Tạo CourseRegistration
   ↓
6. Giáo viên chuẩn bị tài liệu
   - Upload LessonDocumentation
   ↓
7. Bắt đầu lớp học
```

### 2. Quy trình một buổi học điển hình

```
TRƯỚC BUỔI HỌC:
1. Giáo viên xem lesson plan
2. Chuẩn bị tài liệu
3. Upload LessonDocumentation nếu có

TRONG BUỔI HỌC:
4. Điểm danh học viên
   - Check-in qua app (tự động)
   - Hoặc giáo viên điểm danh thủ công
   ↓
5. Tiến hành giảng dạy
   ↓
6. Chụp ảnh hoạt động
   - Upload vào LessonGallery

SAU BUỔI HỌC:
7. Giáo viên đánh giá học viên
   - Chấm 12 tiêu chí
   - Viết nhận xét
   ↓
8. Phụ huynh xem:
   - Attendance record
   - Lesson evaluation
   - Lesson gallery
```

### 3. Quy trình đăng ký học viên mới

```
1. Phụ huynh liên hệ trung tâm
   ↓
2. Staff tiếp nhận thông tin
   ↓
3. Staff tạo Student record
   - Nhập đầy đủ thông tin
   - Upload avatar
   ↓
4. Staff tạo CourseRegistration
   - Chọn lớp học phù hợp
   - Nhập học phí
   ↓
5. Kiểm tra thanh toán
   - Cập nhật paid_amount
   - Hệ thống tự động update payment_status
   ↓
6. Học viên được approved
   - Nhận thông tin đăng nhập app
   - Phụ huynh theo dõi trên app
```

### 4. Quy trình thanh toán học phí

```
1. Học viên đăng ký lớp
   - amount: 5,000,000 VND
   - paid_amount: 0
   - payment_status: unpaid
   ↓
2. Thanh toán lần 1: 2,000,000 VND
   - Cập nhật paid_amount = 2,000,000
   - payment_status → partially_paid (tự động)
   ↓
3. Thanh toán lần 2: 3,000,000 VND
   - Cập nhật paid_amount = 5,000,000
   - payment_status → fully_paid (tự động)
```

### 5. Phân quyền và bảo mật

#### Role-Based Access Control

**Root (Quản trị viên cao nhất)**
- Quản lý users: tạo, sửa, xóa
- Quản lý toàn bộ hệ thống
- Xem tất cả dữ liệu

**Manager (Quản lý viên)**
- Quản lý khóa học, lớp học
- Quản lý học viên, đăng ký
- Xem báo cáo
- Không thể quản lý users

**Teacher (Giáo viên)**
- Xem lớp học được phân công
- Điểm danh học viên
- Đánh giá học viên
- Upload tài liệu, gallery
- Không thể chỉnh sửa thông tin lớp học

**Teaching Assistant (Trợ giảng)**
- Tương tự Teacher
- Hỗ trợ điểm danh, upload tài liệu
- Không được đánh giá học viên

#### Middleware Authentication
```python
# Web Authentication (JWT)
- Kiểm tra JWT token trong header
- Xác thực WebUser
- Kiểm tra role và permissions

# App Authentication
- Kiểm tra app token
- Xác thực AppUser
- Link với Student/Parent
```

---

## PHỤ LỤC

### A. Biến môi trường (Environment Variables)

```bash
# Database Configuration
DATABASE_ENGINE=mysql              # Database engine (mysql/postgresql)
DATABASE_NAME=steam               # Database name
DATABASE_USER=root                # Database user
DATABASE_PASSWORD=password        # Database password
DATABASE_HOST=localhost           # Database host
DATABASE_PORT=3306               # Database port

# Redis Configuration
REDIS_HOST=localhost             # Redis host
REDIS_PORT=6379                 # Redis port
REDIS_USERNAME=                 # Redis username (optional)
REDIS_PASSWORD=                 # Redis password (optional)

# Email Configuration
EMAIL_HOST=smtp.gmail.com       # SMTP server
EMAIL_PORT=587                  # SMTP port
EMAIL_HOST_USER=email@gmail.com # Email account
EMAIL_HOST_PASSWORD=password    # Email password or app password

# Logging Configuration (BetterStack)
BETTERSTACK_LOG_TOKEN=token     # BetterStack log token
BETTERSTACK_LOG_HOST=host       # BetterStack log host

# Google Drive Configuration
GDRIVE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json
GDRIVE_DEFAULT_FOLDER_ID=folder-id
```

### B. Các lệnh Django thường dùng

```bash
# Database
python manage.py makemigrations              # Tạo migration files
python manage.py migrate                     # Chạy migrations
python manage.py showmigrations             # Xem trạng thái migrations
python manage.py sqlmigrate app_name 0001   # Xem SQL của migration

# Users
python manage.py createsuperuser            # Tạo superuser
python manage.py changepassword username    # Đổi password

# Shell & Debug
python manage.py shell                      # Django shell
python manage.py dbshell                    # Database shell
python manage.py check                      # Kiểm tra lỗi

# Static Files
python manage.py collectstatic              # Thu thập static files
python manage.py findstatic filename        # Tìm static file

# Testing
python manage.py test                       # Chạy tests
python manage.py test app_name              # Test specific app

# Custom
python manage.py flush                      # Xóa tất cả dữ liệu
python manage.py dumpdata > backup.json     # Backup data
python manage.py loaddata backup.json       # Restore data
```

### C. Troubleshooting

#### Lỗi kết nối MySQL
```bash
# Kiểm tra MySQL đang chạy
# macOS
brew services list | grep mysql

# Ubuntu
sudo systemctl status mysql

# Test connection
mysql -u root -p -h localhost
```

#### Lỗi kết nối Redis
```bash
# Kiểm tra Redis đang chạy
redis-cli ping
# Response: PONG

# Xem thông tin Redis
redis-cli info
```

#### Lỗi migration
```bash
# Reset migrations (CẢNH BÁO: Mất dữ liệu)
python manage.py migrate app_name zero
python manage.py migrate app_name

# Fake migrations (nếu DB đã có schema)
python manage.py migrate --fake
```

#### Lỗi import PyMySQL
```bash
# Kiểm tra __init__.py trong steam/
cat steam/__init__.py

# Phải có:
import pymysql
pymysql.install_as_MySQLdb()
```

### D. Performance Tips

#### Caching
```python
# Cache view results
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache 15 minutes
def my_view(request):
    ...
```

#### Database Optimization
```python
# Use select_related for ForeignKey
students = Student.objects.select_related('class_room').all()

# Use prefetch_related for ManyToMany / reverse FK
classes = ClassRoom.objects.prefetch_related('students').all()

# Index important fields
class Meta:
    indexes = [
        models.Index(fields=['email']),
        models.Index(fields=['created_at']),
    ]
```

### E. Deployment Checklist

```bash
☐ Set DEBUG=False in production
☐ Set SECRET_KEY to random value
☐ Configure ALLOWED_HOSTS
☐ Set up HTTPS/SSL
☐ Configure CORS properly
☐ Set up database backups
☐ Configure logging
☐ Set up monitoring
☐ Use environment variables for secrets
☐ Run collectstatic
☐ Set up Gunicorn/uWSGI
☐ Set up Nginx reverse proxy
☐ Configure firewall
☐ Set up automated backups
```

### F. Liên hệ & Hỗ trợ

- **Email**: support@bdu.edu.vn
- **Địa chỉ**: Trường Đại học Bình Dương
- **Website**: https://bdu.edu.vn

---

## CHANGELOG

### Version 1.0.0 (2025-11-30)
- Khởi tạo dự án
- Các chức năng chính:
  - Quản lý khóa học, lớp học
  - Quản lý học viên
  - Điểm danh
  - Đánh giá học viên (12 tiêu chí)
  - Quản lý tài liệu, gallery
  - Quản lý cơ sở vật chất
  - Tin tức & thông báo
- API cho Web và Mobile App
- JWT Authentication
- Google Drive integration
- Redis caching
- BetterStack logging

---

## LICENSE

Copyright © 2025 Bình Dương University. All rights reserved.

---

**Tài liệu này được tạo tự động và cập nhật thường xuyên. Vui lòng kiểm tra version mới nhất.**

