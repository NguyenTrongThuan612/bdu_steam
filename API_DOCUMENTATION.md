# TÀI LIỆU API CHI TIẾT

## MỤC LỤC
1. [Tổng quan](#tổng-quan)
2. [Authentication APIs](#authentication-apis)
3. [User Management APIs](#user-management-apis)
4. [Student Management APIs](#student-management-apis)
5. [Course Management APIs](#course-management-apis)
6. [Class Management APIs](#class-management-apis)
7. [Lesson Management APIs](#lesson-management-apis)
8. [Attendance APIs](#attendance-apis)
9. [Evaluation APIs](#evaluation-apis)
10. [Facility APIs](#facility-apis)
11. [News APIs](#news-apis)
12. [Mobile App APIs](#mobile-app-apis)

---

## TỔNG QUAN

### Base URLs
- **Back-Office (Web Admin)**: `http://localhost:8000/back-office/`
- **Mobile App**: `http://localhost:8000/app/`
- **Health Check**: `http://localhost:8000/health/`
- **API Documentation**: `http://localhost:8000/swagger/`

### Authentication
Tất cả APIs (trừ login/register) yêu cầu JWT token trong header:
```
Authorization: Bearer <access_token>
```

### Common HTTP Status Codes
```
200 OK              - Request thành công
201 Created         - Tạo resource thành công
204 No Content      - Xóa thành công
400 Bad Request     - Lỗi validation
401 Unauthorized    - Chưa đăng nhập
403 Forbidden       - Không có quyền
404 Not Found       - Không tìm thấy
500 Server Error    - Lỗi server
```

### Pagination
Các list APIs có pagination với format:
```json
{
  "count": 150,
  "next": "http://localhost:8000/back-office/students?page=2",
  "previous": null,
  "results": [...]
}
```

Query parameters:
- `page`: Số trang (default: 1)
- `page_size`: Số items/trang (default: 20, max: 100)

---

## AUTHENTICATION APIs

### 1. Web Login (Back-Office)

**Endpoint**: `POST /back-office/auth/login`

**Description**: Đăng nhập cho admin, manager, teacher

**Request Body**:
```json
{
  "email": "admin@bdu.edu.vn",
  "password": "SecurePassword123"
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@bdu.edu.vn",
    "name": "Administrator",
    "staff_id": "BDU001",
    "role": "root",
    "status": "activated",
    "phone": "0901234567",
    "gender": "male",
    "birth_date": "1990-01-01"
  }
}
```

**Error Responses**:
```json
// 401 Unauthorized - Invalid credentials
{
  "detail": "Invalid email or password"
}

// 403 Forbidden - Account not activated
{
  "detail": "Account is not activated"
}
```

### 2. Refresh Token

**Endpoint**: `POST /back-office/auth/refresh`

**Description**: Lấy access token mới

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Register User (Root Only)

**Endpoint**: `POST /back-office/auth/register`

**Permission**: Root only

**Request Body**:
```json
{
  "email": "teacher@bdu.edu.vn",
  "password": "SecurePassword123",
  "name": "Nguyen Van A",
  "staff_id": "BDU002",
  "role": "teacher",
  "phone": "0901234567",
  "gender": "male",
  "birth_date": "1985-05-15"
}
```

**Success Response** (201 Created):
```json
{
  "id": 2,
  "email": "teacher@bdu.edu.vn",
  "name": "Nguyen Van A",
  "staff_id": "BDU002",
  "role": "teacher",
  "status": "activated",
  "phone": "0901234567",
  "gender": "male",
  "birth_date": "1985-05-15"
}
```

### 4. Forgot Password

**Endpoint**: `POST /back-office/auth/forgot-password`

**Description**: Gửi OTP qua email

**Request Body**:
```json
{
  "email": "teacher@bdu.edu.vn"
}
```

**Success Response** (200 OK):
```json
{
  "message": "OTP has been sent to your email",
  "email": "teacher@bdu.edu.vn"
}
```

### 5. Reset Password

**Endpoint**: `POST /back-office/auth/reset-password`

**Description**: Đặt lại mật khẩu với OTP

**Request Body**:
```json
{
  "email": "teacher@bdu.edu.vn",
  "otp": "123456",
  "new_password": "NewSecurePassword123"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Password has been reset successfully"
}
```

### 6. Logout

**Endpoint**: `POST /back-office/auth/logout`

**Headers**: 
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## USER MANAGEMENT APIs

### 1. List Users

**Endpoint**: `GET /back-office/users`

**Permission**: Root, Manager

**Query Parameters**:
- `search`: Tìm kiếm theo name, email, staff_id
- `role`: Filter theo role (root/manager/teacher)
- `status`: Filter theo status (activated/blocked/unverified)
- `ordering`: Sắp xếp (name, email, created_at, -created_at)

**Example**: `GET /back-office/users?role=teacher&status=activated&ordering=-created_at`

**Success Response** (200 OK):
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "email": "teacher1@bdu.edu.vn",
      "name": "Nguyen Van A",
      "staff_id": "BDU002",
      "role": "teacher",
      "status": "activated",
      "phone": "0901234567",
      "gender": "male",
      "birth_date": "1985-05-15",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    },
    ...
  ]
}
```

### 2. Get User Detail

**Endpoint**: `GET /back-office/users/{id}`

**Permission**: Root, Manager

**Success Response** (200 OK):
```json
{
  "id": 2,
  "email": "teacher1@bdu.edu.vn",
  "name": "Nguyen Van A",
  "staff_id": "BDU002",
  "role": "teacher",
  "status": "activated",
  "phone": "0901234567",
  "gender": "male",
  "birth_date": "1985-05-15",
  "teaching_classes": [
    {
      "id": 1,
      "name": "STEAM-101",
      "course_name": "Introduction to STEAM"
    }
  ],
  "assisting_classes": [
    {
      "id": 2,
      "name": "STEAM-102",
      "course_name": "Advanced STEAM"
    }
  ],
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

### 3. Update User

**Endpoint**: `PUT /back-office/users/{id}`

**Permission**: Root only

**Request Body**:
```json
{
  "name": "Nguyen Van A Updated",
  "phone": "0901234568",
  "status": "activated",
  "role": "teacher"
}
```

**Success Response** (200 OK):
```json
{
  "id": 2,
  "email": "teacher1@bdu.edu.vn",
  "name": "Nguyen Van A Updated",
  "staff_id": "BDU002",
  "role": "teacher",
  "status": "activated",
  "phone": "0901234568",
  ...
}
```

### 4. Delete User

**Endpoint**: `DELETE /back-office/users/{id}`

**Permission**: Root only

**Success Response** (204 No Content)

---

## STUDENT MANAGEMENT APIs

### 1. List Students

**Endpoint**: `GET /back-office/students`

**Permission**: Manager, Teacher

**Query Parameters**:
- `search`: Tìm theo name, identification_number, email
- `is_active`: Filter active students (true/false)
- `gender`: Filter theo gender (male/female/other)
- `class_room`: Filter theo class_room_id
- `ordering`: Sắp xếp

**Example**: `GET /back-office/students?is_active=true&class_room=5&search=nguyen`

**Success Response** (200 OK):
```json
{
  "count": 45,
  "next": "http://localhost:8000/back-office/students?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "identification_number": "001234567890",
      "first_name": "Nguyen",
      "last_name": "Van An",
      "full_name": "Nguyen Van An",
      "date_of_birth": "2015-06-15",
      "age": 9,
      "gender": "male",
      "address": "123 Le Loi, Binh Duong",
      "phone_number": "0901234567",
      "email": "parent@example.com",
      "parent_name": "Nguyen Van B",
      "parent_phone": "0901234567",
      "parent_email": "parent@example.com",
      "avatar_url": "https://drive.google.com/...",
      "is_active": true,
      "note": "Học sinh ngoan",
      "current_classes": [
        {
          "id": 5,
          "name": "STEAM-101",
          "course_name": "Introduction to STEAM"
        }
      ],
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-15T14:30:00Z"
    },
    ...
  ]
}
```

### 2. Create Student

**Endpoint**: `POST /back-office/students`

**Permission**: Manager

**Request Body**:
```json
{
  "identification_number": "001234567890",
  "first_name": "Nguyen",
  "last_name": "Van An",
  "date_of_birth": "2015-06-15",
  "gender": "male",
  "address": "123 Le Loi, Binh Duong",
  "phone_number": "0901234567",
  "email": "student@example.com",
  "parent_name": "Nguyen Van B",
  "parent_phone": "0901234567",
  "parent_email": "parent@example.com",
  "note": "Học sinh ngoan"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "identification_number": "001234567890",
  "first_name": "Nguyen",
  "last_name": "Van An",
  "full_name": "Nguyen Van An",
  "date_of_birth": "2015-06-15",
  "age": 9,
  "gender": "male",
  "is_active": true,
  ...
}
```

### 3. Update Student

**Endpoint**: `PUT /back-office/students/{id}` or `PATCH /back-office/students/{id}`

**Permission**: Manager

**Request Body** (PATCH - partial update):
```json
{
  "phone_number": "0901234568",
  "address": "456 Nguyen Trai, Binh Duong"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "identification_number": "001234567890",
  "first_name": "Nguyen",
  "last_name": "Van An",
  "phone_number": "0901234568",
  "address": "456 Nguyen Trai, Binh Duong",
  ...
}
```

### 4. Delete Student (Soft Delete)

**Endpoint**: `DELETE /back-office/students/{id}`

**Permission**: Manager

**Success Response** (204 No Content)

### 5. Upload Student Avatar

**Endpoint**: `POST /back-office/students/{id}/upload-avatar`

**Permission**: Manager

**Content-Type**: `multipart/form-data`

**Request Body**:
```
avatar: <file>
```

**Success Response** (200 OK):
```json
{
  "avatar_url": "https://drive.google.com/file/d/..."
}
```

---

## COURSE MANAGEMENT APIs

### 1. List Courses

**Endpoint**: `GET /back-office/courses`

**Permission**: All authenticated users

**Query Parameters**:
- `search`: Tìm theo name, description
- `is_active`: Filter active courses
- `ordering`: Sắp xếp

**Success Response** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Introduction to STEAM",
      "description": "Khóa học giới thiệu về STEAM cho trẻ em 6-8 tuổi",
      "thumbnail_url": "https://drive.google.com/...",
      "price": "5000000.00",
      "duration": 720,
      "is_active": true,
      "total_classes": 3,
      "active_classes": 2,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    },
    ...
  ]
}
```

### 2. Create Course

**Endpoint**: `POST /back-office/courses`

**Permission**: Manager

**Request Body**:
```json
{
  "name": "Introduction to STEAM",
  "description": "Khóa học giới thiệu về STEAM cho trẻ em 6-8 tuổi",
  "thumbnail_url": "https://drive.google.com/...",
  "price": "5000000.00",
  "duration": 720,
  "is_active": true
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "name": "Introduction to STEAM",
  "description": "Khóa học giới thiệu về STEAM cho trẻ em 6-8 tuổi",
  "thumbnail_url": "https://drive.google.com/...",
  "price": "5000000.00",
  "duration": 720,
  "is_active": true,
  "total_classes": 0,
  "active_classes": 0,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

### 3. Get Course Detail

**Endpoint**: `GET /back-office/courses/{id}`

**Permission**: All authenticated users

**Success Response** (200 OK):
```json
{
  "id": 1,
  "name": "Introduction to STEAM",
  "description": "Khóa học giới thiệu về STEAM cho trẻ em 6-8 tuổi",
  "thumbnail_url": "https://drive.google.com/...",
  "price": "5000000.00",
  "duration": 720,
  "is_active": true,
  "classes": [
    {
      "id": 1,
      "name": "STEAM-101-2025-01",
      "start_date": "2025-01-15",
      "end_date": "2025-03-15",
      "teacher": {
        "id": 2,
        "name": "Nguyen Van A"
      },
      "current_students": 15,
      "max_students": 20,
      "is_active": true
    }
  ],
  "total_classes": 3,
  "active_classes": 2,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

---

## CLASS MANAGEMENT APIs

### 1. List Classes

**Endpoint**: `GET /back-office/classes`

**Permission**: All authenticated users

**Query Parameters**:
- `course`: Filter theo course_id
- `teacher`: Filter theo teacher_id
- `is_active`: Filter active classes
- `start_date_from`: Filter classes starting from date
- `start_date_to`: Filter classes starting to date

**Success Response** (200 OK):
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "STEAM-101-2025-01",
      "description": "Lớp học STEAM tháng 1/2025",
      "thumbnail_url": "https://...",
      "course": {
        "id": 1,
        "name": "Introduction to STEAM",
        "price": "5000000.00"
      },
      "teacher": {
        "id": 2,
        "name": "Nguyen Van A",
        "email": "teacher@bdu.edu.vn"
      },
      "teaching_assistant": {
        "id": 3,
        "name": "Tran Thi B",
        "email": "ta@bdu.edu.vn"
      },
      "max_students": 20,
      "current_students": 15,
      "available_slots": 5,
      "start_date": "2025-01-15",
      "end_date": "2025-03-15",
      "schedule": {
        "monday": [
          {"start_time": "08:00", "end_time": "10:00"}
        ],
        "wednesday": [
          {"start_time": "08:00", "end_time": "10:00"}
        ],
        "friday": [
          {"start_time": "08:00", "end_time": "10:00"}
        ]
      },
      "total_sessions": 24,
      "is_active": true,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    },
    ...
  ]
}
```

### 2. Create Class

**Endpoint**: `POST /back-office/classes`

**Permission**: Manager

**Request Body**:
```json
{
  "name": "STEAM-101-2025-01",
  "description": "Lớp học STEAM tháng 1/2025",
  "course_id": 1,
  "teacher_id": 2,
  "teaching_assistant_id": 3,
  "max_students": 20,
  "start_date": "2025-01-15",
  "end_date": "2025-03-15",
  "schedule": {
    "monday": [
      {"start_time": "08:00", "end_time": "10:00"}
    ],
    "wednesday": [
      {"start_time": "08:00", "end_time": "10:00"}
    ],
    "friday": [
      {"start_time": "08:00", "end_time": "10:00"}
    ]
  },
  "is_active": true
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "name": "STEAM-101-2025-01",
  "description": "Lớp học STEAM tháng 1/2025",
  "course": {...},
  "teacher": {...},
  "teaching_assistant": {...},
  "max_students": 20,
  "current_students": 0,
  "available_slots": 20,
  "start_date": "2025-01-15",
  "end_date": "2025-03-15",
  "schedule": {...},
  "total_sessions": 0,
  "is_active": true,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

### 3. Get Class Detail

**Endpoint**: `GET /back-office/classes/{id}`

**Permission**: All authenticated users

**Success Response** (200 OK):
```json
{
  "id": 1,
  "name": "STEAM-101-2025-01",
  "description": "Lớp học STEAM tháng 1/2025",
  "course": {
    "id": 1,
    "name": "Introduction to STEAM",
    "price": "5000000.00"
  },
  "teacher": {...},
  "teaching_assistant": {...},
  "modules": [
    {
      "id": 1,
      "name": "Module 1: Giới thiệu",
      "sequence_number": 1,
      "total_lessons": 4,
      "lessons": [
        {
          "id": 1,
          "name": "Lesson 1: Làm quen STEAM",
          "sequence_number": 1,
          "start_datetime": "2025-01-15T08:00:00+07:00",
          "end_datetime": "2025-01-15T10:00:00+07:00",
          "status": "completed"
        },
        ...
      ]
    },
    ...
  ],
  "students": [
    {
      "id": 1,
      "full_name": "Nguyen Van An",
      "registration": {
        "id": 1,
        "status": "approved",
        "amount": "5000000.00",
        "paid_amount": "5000000.00",
        "payment_status": "fully_paid"
      }
    },
    ...
  ],
  "max_students": 20,
  "current_students": 15,
  "available_slots": 5,
  "start_date": "2025-01-15",
  "end_date": "2025-03-15",
  "schedule": {...},
  "total_sessions": 24,
  "is_active": true,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

---

## LESSON MANAGEMENT APIs

### 1. List Lessons

**Endpoint**: `GET /back-office/lessons`

**Permission**: Teacher, Manager

**Query Parameters**:
- `class_room`: Filter theo class_room_id
- `module`: Filter theo module_id
- `status`: Filter theo status (not_started/in_progress/completed)
- `date_from`: Filter lessons từ ngày
- `date_to`: Filter lessons đến ngày

**Success Response** (200 OK):
```json
{
  "count": 24,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "module": {
        "id": 1,
        "name": "Module 1: Giới thiệu",
        "class_room": {
          "id": 1,
          "name": "STEAM-101-2025-01"
        }
      },
      "name": "Lesson 1: Làm quen STEAM",
      "sequence_number": 1,
      "start_datetime": "2025-01-15T08:00:00+07:00",
      "end_datetime": "2025-01-15T10:00:00+07:00",
      "status": "completed",
      "attendance_count": 15,
      "evaluation_count": 15,
      "gallery_count": 5,
      "documentation_count": 2,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-15T12:00:00Z"
    },
    ...
  ]
}
```

### 2. Get Lesson Detail

**Endpoint**: `GET /back-office/lessons/{id}`

**Permission**: Teacher, Manager

**Success Response** (200 OK):
```json
{
  "id": 1,
  "module": {
    "id": 1,
    "name": "Module 1: Giới thiệu",
    "sequence_number": 1,
    "class_room": {
      "id": 1,
      "name": "STEAM-101-2025-01",
      "teacher": {
        "id": 2,
        "name": "Nguyen Van A"
      }
    }
  },
  "name": "Lesson 1: Làm quen STEAM",
  "sequence_number": 1,
  "start_datetime": "2025-01-15T08:00:00+07:00",
  "end_datetime": "2025-01-15T10:00:00+07:00",
  "status": "completed",
  "attendances": [
    {
      "id": 1,
      "student": {
        "id": 1,
        "full_name": "Nguyen Van An"
      },
      "status": "present",
      "check_in_time": "2025-01-15T07:55:00+07:00",
      "note": ""
    },
    ...
  ],
  "evaluations": [
    {
      "id": 1,
      "student": {
        "id": 1,
        "full_name": "Nguyen Van An"
      },
      "focus_score": 4,
      "punctuality_score": 5,
      "interaction_score": 4,
      ...
      "comment": "Học sinh rất tích cực"
    },
    ...
  ],
  "gallery": [
    {
      "id": 1,
      "image_url": "https://drive.google.com/...",
      "caption": "Hoạt động nhóm",
      "uploaded_at": "2025-01-15T10:30:00+07:00"
    },
    ...
  ],
  "documentations": [
    {
      "id": 1,
      "file_url": "https://drive.google.com/...",
      "file_name": "Lesson1_Slides.pdf",
      "uploaded_at": "2025-01-14T15:00:00+07:00"
    },
    ...
  ],
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

---

## ATTENDANCE APIs

### 1. Check-in for Lesson

**Endpoint**: `POST /back-office/lesson-checkins`

**Permission**: Teacher, Teaching Assistant

**Description**: Điểm danh hàng loạt cho một buổi học

**Request Body**:
```json
{
  "lesson_id": 1,
  "attendances": [
    {
      "student_id": 1,
      "status": "present"
    },
    {
      "student_id": 2,
      "status": "late",
      "note": "Đến muộn 15 phút"
    },
    {
      "student_id": 3,
      "status": "absent",
      "note": "Xin phép ốm"
    }
  ]
}
```

**Success Response** (201 Created):
```json
{
  "lesson_id": 1,
  "total_students": 15,
  "checked_in": 3,
  "attendances": [
    {
      "id": 1,
      "student": {
        "id": 1,
        "full_name": "Nguyen Van An"
      },
      "status": "present",
      "check_in_time": "2025-01-15T08:00:00+07:00",
      "note": ""
    },
    ...
  ]
}
```

### 2. Update Attendance

**Endpoint**: `PUT /back-office/attendances/{id}`

**Permission**: Teacher, Teaching Assistant

**Request Body**:
```json
{
  "status": "late",
  "note": "Đến muộn 10 phút"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "student": {
    "id": 1,
    "full_name": "Nguyen Van An"
  },
  "lesson": {
    "id": 1,
    "name": "Lesson 1: Làm quen STEAM"
  },
  "status": "late",
  "check_in_time": "2025-01-15T08:10:00+07:00",
  "note": "Đến muộn 10 phút",
  "created_at": "2025-01-15T08:00:00+07:00",
  "updated_at": "2025-01-15T08:15:00+07:00"
}
```

---

## EVALUATION APIs

### 1. Get Evaluation Criteria

**Endpoint**: `GET /back-office/evaluation-criteria`

**Permission**: All authenticated users

**Success Response** (200 OK):
```json
{
  "criteria": [
    {
      "key": "focus_score",
      "name": "Mức độ tập trung",
      "description": "Đánh giá khả năng tập trung của học viên trong buổi học",
      "scale": [
        {"value": 1, "label": "Không tập trung"},
        {"value": 2, "label": "Ít tập trung"},
        {"value": 3, "label": "Tập trung khá"},
        {"value": 4, "label": "Tập trung tốt"},
        {"value": 5, "label": "Hoàn toàn tập trung"}
      ]
    },
    {
      "key": "punctuality_score",
      "name": "Đi muộn/Trễ",
      "description": "Đánh giá tính đúng giờ của học viên",
      "scale": [
        {"value": 1, "label": "Thường xuyên đi muộn/về sớm"},
        {"value": 2, "label": "Hay đi muộn/về sớm"},
        {"value": 3, "label": "Thỉnh thoảng đi muộn/về sớm"},
        {"value": 4, "label": "Hiếm khi đi muộn/về sớm"},
        {"value": 5, "label": "Luôn đúng giờ"}
      ]
    },
    ...
  ]
}
```

### 2. Create/Update Evaluation

**Endpoint**: `POST /back-office/lesson-evaluations`

**Permission**: Teacher

**Description**: Tạo hoặc cập nhật đánh giá (upsert)

**Request Body**:
```json
{
  "lesson_id": 1,
  "student_id": 1,
  "focus_score": 4,
  "punctuality_score": 5,
  "interaction_score": 4,
  "project_idea_score": 4,
  "critical_thinking_score": 3,
  "teamwork_score": 5,
  "idea_sharing_score": 4,
  "creativity_score": 4,
  "communication_score": 4,
  "homework_score": 5,
  "old_knowledge_score": 4,
  "new_knowledge_score": 4,
  "comment": "Học sinh rất tích cực và có ý tưởng sáng tạo"
}
```

**Success Response** (201 Created hoặc 200 OK):
```json
{
  "id": 1,
  "lesson": {
    "id": 1,
    "name": "Lesson 1: Làm quen STEAM"
  },
  "student": {
    "id": 1,
    "full_name": "Nguyen Van An"
  },
  "focus_score": 4,
  "punctuality_score": 5,
  "interaction_score": 4,
  "project_idea_score": 4,
  "critical_thinking_score": 3,
  "teamwork_score": 5,
  "idea_sharing_score": 4,
  "creativity_score": 4,
  "communication_score": 4,
  "homework_score": 5,
  "old_knowledge_score": 4,
  "new_knowledge_score": 4,
  "average_score": 4.17,
  "comment": "Học sinh rất tích cực và có ý tưởng sáng tạo",
  "created_at": "2025-01-15T12:00:00+07:00",
  "updated_at": "2025-01-15T12:00:00+07:00"
}
```

---

## FACILITY APIs

### 1. List Facilities

**Endpoint**: `GET /back-office/facilities`

**Permission**: All users

**Success Response** (200 OK):
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Phòng học A1",
      "description": "Phòng học rộng 50m2, trang bị đầy đủ thiết bị STEAM",
      "images": [
        {
          "id": 1,
          "image_url": "https://drive.google.com/...",
          "caption": "Toàn cảnh phòng học"
        },
        {
          "id": 2,
          "image_url": "https://drive.google.com/...",
          "caption": "Góc thực hành"
        }
      ],
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    },
    ...
  ]
}
```

### 2. Create Facility

**Endpoint**: `POST /back-office/facilities`

**Permission**: Manager

**Request Body**:
```json
{
  "name": "Phòng học A1",
  "description": "Phòng học rộng 50m2, trang bị đầy đủ thiết bị STEAM"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "name": "Phòng học A1",
  "description": "Phòng học rộng 50m2, trang bị đầy đủ thiết bị STEAM",
  "images": [],
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

### 3. Upload Facility Image

**Endpoint**: `POST /back-office/facility-images`

**Permission**: Manager

**Content-Type**: `multipart/form-data`

**Request Body**:
```
facility_id: 1
image: <file>
caption: "Toàn cảnh phòng học"
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "facility_id": 1,
  "image_url": "https://drive.google.com/...",
  "caption": "Toàn cảnh phòng học",
  "created_at": "2025-01-01T10:30:00Z"
}
```

---

## NEWS APIs

### 1. List News

**Endpoint**: `GET /back-office/news`

**Permission**: All users

**Success Response** (200 OK):
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Khai giảng khóa học STEAM mới",
      "link": "https://bdu.edu.vn/news/khai-giang-khoa-hoc-steam",
      "image": "https://bdu.edu.vn/images/news1.jpg",
      "posted_at": "2025-01-15T10:00:00+07:00",
      "created_at": "2025-01-15T09:00:00+07:00",
      "updated_at": "2025-01-15T09:00:00+07:00"
    },
    ...
  ]
}
```

### 2. Create News

**Endpoint**: `POST /back-office/news`

**Permission**: Manager

**Request Body**:
```json
{
  "title": "Khai giảng khóa học STEAM mới",
  "link": "https://bdu.edu.vn/news/khai-giang-khoa-hoc-steam",
  "image": "https://bdu.edu.vn/images/news1.jpg",
  "posted_at": "2025-01-15T10:00:00+07:00"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "title": "Khai giảng khóa học STEAM mới",
  "link": "https://bdu.edu.vn/news/khai-giang-khoa-hoc-steam",
  "image": "https://bdu.edu.vn/images/news1.jpg",
  "posted_at": "2025-01-15T10:00:00+07:00",
  "created_at": "2025-01-15T09:00:00+07:00",
  "updated_at": "2025-01-15T09:00:00+07:00"
}
```

---

## MOBILE APP APIs

### 1. App Login

**Endpoint**: `POST /app/auth/login`

**Description**: Đăng nhập cho mobile app (phụ huynh, giáo viên)

**Request Body**:
```json
{
  "app_user_id": "firebase_uid_123",
  "name": "Nguyen Van C",
  "avatar_url": "https://...",
  "phone_number": "0901234567"
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "app_user": {
    "id": 1,
    "app_user_id": "firebase_uid_123",
    "name": "Nguyen Van C",
    "avatar_url": "https://...",
    "phone_number": "0901234567"
  }
}
```

### 2. Get Courses (App)

**Endpoint**: `GET /app/courses`

**Permission**: App user authenticated

**Success Response** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Introduction to STEAM",
      "description": "Khóa học giới thiệu về STEAM cho trẻ em 6-8 tuổi",
      "thumbnail_url": "https://...",
      "price": "5000000.00",
      "duration": 720,
      "active_classes_count": 2
    },
    ...
  ]
}
```

### 3. Get Time Table (App)

**Endpoint**: `GET /app/time-tables`

**Permission**: App user authenticated

**Query Parameters**:
- `student_id`: ID học viên
- `date_from`: Từ ngày
- `date_to`: Đến ngày

**Example**: `GET /app/time-tables?student_id=1&date_from=2025-01-15&date_to=2025-01-22`

**Success Response** (200 OK):
```json
{
  "student": {
    "id": 1,
    "full_name": "Nguyen Van An"
  },
  "schedule": [
    {
      "date": "2025-01-15",
      "day_of_week": "Monday",
      "lessons": [
        {
          "id": 1,
          "name": "Lesson 1: Làm quen STEAM",
          "class": {
            "id": 1,
            "name": "STEAM-101-2025-01"
          },
          "start_time": "08:00",
          "end_time": "10:00",
          "start_datetime": "2025-01-15T08:00:00+07:00",
          "end_datetime": "2025-01-15T10:00:00+07:00",
          "status": "completed",
          "attendance": {
            "status": "present",
            "check_in_time": "2025-01-15T07:55:00+07:00"
          },
          "evaluation": {
            "average_score": 4.17,
            "comment": "Học sinh rất tích cực"
          }
        }
      ]
    },
    {
      "date": "2025-01-17",
      "day_of_week": "Wednesday",
      "lessons": [...]
    }
  ]
}
```

### 4. Check-in (App)

**Endpoint**: `POST /app/attendances/check-in`

**Permission**: App user authenticated

**Request Body**:
```json
{
  "lesson_id": 2,
  "student_id": 1
}
```

**Success Response** (201 Created):
```json
{
  "id": 2,
  "student": {
    "id": 1,
    "full_name": "Nguyen Van An"
  },
  "lesson": {
    "id": 2,
    "name": "Lesson 2: Khám phá khoa học"
  },
  "status": "present",
  "check_in_time": "2025-01-17T07:58:00+07:00",
  "message": "Check-in successful"
}
```

### 5. Get Student Evaluations (App)

**Endpoint**: `GET /app/lesson-evaluations`

**Permission**: App user authenticated

**Query Parameters**:
- `student_id`: ID học viên
- `class_room`: ID lớp học
- `date_from`: Từ ngày
- `date_to`: Đến ngày

**Example**: `GET /app/lesson-evaluations?student_id=1&class_room=1`

**Success Response** (200 OK):
```json
{
  "student": {
    "id": 1,
    "full_name": "Nguyen Van An"
  },
  "class_room": {
    "id": 1,
    "name": "STEAM-101-2025-01"
  },
  "evaluations": [
    {
      "id": 1,
      "lesson": {
        "id": 1,
        "name": "Lesson 1: Làm quen STEAM",
        "date": "2025-01-15"
      },
      "scores": {
        "focus_score": 4,
        "punctuality_score": 5,
        "interaction_score": 4,
        "project_idea_score": 4,
        "critical_thinking_score": 3,
        "teamwork_score": 5,
        "idea_sharing_score": 4,
        "creativity_score": 4,
        "communication_score": 4,
        "homework_score": 5,
        "old_knowledge_score": 4,
        "new_knowledge_score": 4
      },
      "average_score": 4.17,
      "comment": "Học sinh rất tích cực và có ý tưởng sáng tạo",
      "evaluated_at": "2025-01-15T12:00:00+07:00"
    },
    ...
  ],
  "summary": {
    "total_lessons": 5,
    "evaluated_lessons": 5,
    "overall_average": 4.25,
    "strongest_criteria": [
      {"key": "teamwork_score", "name": "Hợp tác nhóm", "average": 4.8},
      {"key": "punctuality_score", "name": "Đúng giờ", "average": 4.6}
    ],
    "weakest_criteria": [
      {"key": "critical_thinking_score", "name": "Tư duy phản biện", "average": 3.4}
    ]
  }
}
```

---

## ERROR HANDLING

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": ["Error detail"]
  }
}
```

### Common Error Codes

```
INVALID_CREDENTIALS       - Email hoặc password không đúng
ACCOUNT_NOT_ACTIVATED     - Tài khoản chưa được kích hoạt
ACCOUNT_BLOCKED           - Tài khoản bị khóa
INVALID_TOKEN             - Token không hợp lệ
TOKEN_EXPIRED             - Token hết hạn
PERMISSION_DENIED         - Không có quyền truy cập
RESOURCE_NOT_FOUND        - Không tìm thấy resource
VALIDATION_ERROR          - Lỗi validation
CLASS_FULL                - Lớp học đã đầy
ALREADY_REGISTERED        - Đã đăng ký lớp này
INVALID_OTP               - OTP không đúng
OTP_EXPIRED               - OTP hết hạn
FILE_TOO_LARGE            - File quá lớn
INVALID_FILE_TYPE         - Loại file không hợp lệ
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-30  
**API Base URL**: `http://localhost:8000`

