# HƯỚNG DẪN NHANH - QUICK START

## Dành cho Developer mới

### ⚡ Setup nhanh trong 5 phút

#### 1. Clone và cài đặt dependencies
```bash
git clone <repository-url>
cd bdu_steam
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### 2. Tạo file `.env`
```bash
cp .env.example .env
# Hoặc tạo thủ công:
```

```env
DATABASE_ENGINE=mysql
DATABASE_NAME=steam
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=3306

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=
REDIS_PASSWORD=

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

BETTERSTACK_LOG_TOKEN=test-token
BETTERSTACK_LOG_HOST=localhost

GDRIVE_SERVICE_ACCOUNT_FILE=./service_account.json
GDRIVE_DEFAULT_FOLDER_ID=
```

#### 3. Setup Database
```bash
# Tạo database trong MySQL
mysql -u root -p
```
```sql
CREATE DATABASE steam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### 4. Chạy migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 5. Chạy server
```bash
python manage.py runserver
```

Truy cập: http://localhost:8000

---

## 🐳 Setup với Docker (Khuyến nghị)

### Chỉ cần 2 lệnh!

```bash
# 1. Build và start
docker-compose up -d

# 2. Setup database (lần đầu)
docker-compose exec steam_backend python manage.py migrate
docker-compose exec steam_backend python manage.py createsuperuser
```

**Xong!** Truy cập: http://localhost:8000

---

## 📚 APIs chính

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/back-office/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@bdu.edu.vn", "password": "password"}'

# Sử dụng token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/back-office/students
```

### Swagger Documentation
Mở browser: http://localhost:8000/swagger/

---

## 🗂️ Cấu trúc Project quan trọng

```
bdu_steam/
├── steam/              # Django settings
│   └── settings.py    # ⚙️ Cấu hình chính
│
├── steam_api/
│   ├── models/        # 📊 Database models
│   ├── serializers/   # 🔄 API serializers
│   ├── views/         # 🎯 API endpoints
│   │   ├── web/       # Back-office APIs
│   │   └── app/       # Mobile APIs
│   ├── middlewares/   # 🔐 Auth & Permissions
│   └── helpers/       # 🛠️ Utilities
│
├── manage.py          # 🚀 Django CLI
├── requirements.txt   # 📦 Dependencies
└── docker-compose.yaml # 🐳 Docker config
```

---

## 🔥 Các lệnh thường dùng

### Django Management
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Create user
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run tests
python manage.py test
```

### Docker
```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose stop

# View logs
docker-compose logs -f steam_backend

# Execute command in container
docker-compose exec steam_backend python manage.py migrate

# Rebuild
docker-compose build --no-cache
```

### Git
```bash
# Tạo branch mới
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature
```

---

## 🎯 Workflow phát triển

### 1. Tạo Model mới
```python
# steam_api/models/my_model.py
from django.db import models

class MyModel(models.Model):
    class Meta:
        db_table = "my_table"
    
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
```

### 2. Tạo Serializer
```python
# steam_api/serializers/my_model.py
from rest_framework import serializers
from steam_api.models.my_model import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
```

### 3. Tạo ViewSet
```python
# steam_api/views/web/my_model.py
from rest_framework import viewsets
from steam_api.models.my_model import MyModel
from steam_api.serializers.my_model import MyModelSerializer

class MyModelView(viewsets.ModelViewSet):
    queryset = MyModel.objects.filter(deleted_at__isnull=True)
    serializer_class = MyModelSerializer
```

### 4. Register URL
```python
# steam_api/urls.py
from steam_api.views.web.my_model import MyModelView

web_router.register('my-models', MyModelView, "my_models")
```

### 5. Chạy migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🐛 Debugging

### Django Debug Toolbar (Development)
```python
# Đã có trong settings.py khi DEBUG=True
# Truy cập bất kỳ trang nào sẽ thấy debug toolbar bên phải
```

### Print Debug trong code
```python
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.info(f"Request from: {request.user}")
    logger.debug(f"Data: {request.data}")
    # ...
```

### Django Shell để test
```bash
python manage.py shell
```
```python
>>> from steam_api.models.student import Student
>>> students = Student.objects.all()
>>> for s in students:
...     print(s.first_name, s.last_name)
```

---

## 📖 Tài liệu đầy đủ

- **README.md**: Tài liệu tổng quan, setup chi tiết
- **ARCHITECTURE.md**: Kiến trúc hệ thống
- **API_DOCUMENTATION.md**: Tài liệu API đầy đủ
- **DEPLOYMENT.md**: Hướng dẫn triển khai production

---

## 💡 Tips

### 1. Sử dụng PyMySQL thay vì mysqlclient
Hệ thống đã được config để dùng PyMySQL (không cần compile). Kiểm tra `steam/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### 2. Soft Delete
Tất cả models đều dùng soft delete. Không bao giờ xóa thật:
```python
# ❌ Không làm thế này
student.delete()

# ✅ Làm thế này
from django.utils import timezone
student.deleted_at = timezone.now()
student.save()
```

### 3. Query active records
```python
# Luôn filter deleted_at
Student.objects.filter(deleted_at__isnull=True)
```

### 4. Test API với curl
```bash
# Lấy token
TOKEN=$(curl -s -X POST http://localhost:8000/back-office/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bdu.edu.vn","password":"password"}' \
  | jq -r '.access')

# Sử dụng token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/back-office/students | jq
```

---

## 🆘 Troubleshooting nhanh

### Port 8000 đã được dùng
```bash
# Kill process trên port 8000
lsof -ti:8000 | xargs kill -9

# Hoặc dùng port khác
python manage.py runserver 8001
```

### MySQL connection refused
```bash
# Check MySQL đang chạy
# macOS
brew services list | grep mysql

# Ubuntu
sudo systemctl status mysql

# Start MySQL
brew services start mysql  # macOS
sudo systemctl start mysql  # Ubuntu
```

### Redis connection error
```bash
# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Ubuntu

# Test Redis
redis-cli ping
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Liên hệ & Support

- **Email**: support@bdu.edu.vn
- **Slack**: #steam-dev channel
- **Documentation**: https://docs.bdu.edu.vn

---

**Chúc bạn code vui vẻ! 🚀**

