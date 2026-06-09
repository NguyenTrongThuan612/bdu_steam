# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Django 5.1 + DRF monolith for BDU's STEAM course management. Backs both a back-office web portal and a parent/teacher mobile app. Vietnamese is the user-facing language (error messages, email templates).

## Commands

All commands assume the venv is activated (`source venv/bin/activate`) and `.env` is present at the repo root (loaded via `python-decouple`).

```bash
# Run dev server (default 0.0.0.0:8000)
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Django shell (handy because there is no test suite — use this to poke models)
python manage.py shell

# Tests (Django's default runner; the repo has no tests yet)
python manage.py test
python manage.py test steam_api.tests.SomeTestCase.test_method  # single test

# Docker (full stack: app + MySQL 8 + Redis 6)
docker-compose up -d
docker-compose exec steam_backend python manage.py migrate
```

API entry points once running:
- Swagger UI: `http://localhost:8000/steam/swagger/`
- All REST endpoints are prefixed `/steam/apis/` — back-office at `/steam/apis/back-office/*`, mobile at `/steam/apis/app/*`, health at `/steam/apis/health/`.

## Architecture

### Two API surfaces, two user models, two auth middlewares

The codebase splits cleanly along "web" (back-office) vs "app" (mobile) lines. This split is the most important thing to understand — almost every concept has parallel implementations:

| Concern | Web (back-office) | App (mobile) |
|---|---|---|
| Views | [steam_api/views/web/](steam_api/views/web/) | [steam_api/views/app/](steam_api/views/app/) |
| URL prefix | `/steam/apis/back-office/` | `/steam/apis/app/` |
| User model | `WebUser` (staff: ROOT/MANAGER/TEACHER) | `AppUser` (Zalo-authenticated parents) |
| Auth middleware | [WebUserAuthentication](steam_api/middlewares/web_authentication.py) | [AppAuthentication](steam_api/middlewares/app_authentication.py) |
| Auth flow | JWT (SimpleJWT) + email/password + OTP verification | Zalo OAuth bearer token → Zalo Graph API lookup |
| Session store | Redis key `web_session:{user_id}:{access\|refresh}:{jti}` | Redis key `app_session:access:{zalo_token}` |

Both auth classes verify the token AND require a matching Redis session entry — i.e. logout works by deleting the cache key, not just by token expiry. When debugging "401 with valid token," check Redis.

`WebUser` is also Django's `AUTH_USER_MODEL` (see [steam/settings.py:238](steam/settings.py#L238)), so `request.user` in web views is a `WebUser` instance; in app views it's an `AppUser`.

### Routing

URL registration lives entirely in [steam_api/urls.py](steam_api/urls.py) — two `SimpleRouter` instances (`app_router` → `app/`, `web_router` → `back-office/`), both `trailing_slash=False`, that register every ViewSet. There is no per-app `urls.py` autodiscovery. When adding a new resource, register it in this file.

The two exceptions to the router/ViewSet pattern are wired with explicit `path(...)` entries: `EvaluationCriteriaView` (`back-office/evaluation-criteria`) and `HealthCheckView` (`health/`). Both are plain `APIView`s — `EvaluationCriteriaView` even returns a raw DRF `Response` (not `RestResponse`), so don't treat it as the template for new endpoints.

### Permissions

Role-based permission classes in [steam_api/middlewares/permissions.py](steam_api/middlewares/permissions.py): `IsRoot`, `IsNotRoot`, `IsManager`, `IsTeacher`. ViewSets typically override `get_permissions()` to vary perms by action (see [steam_api/views/web/course.py:20-23](steam_api/views/web/course.py#L20-L23) for the pattern: `IsManager` for write actions, `IsNotRoot` for reads).

The `IsNotRoot` rule is intentional — ROOT manages users/system config but does not interact with course/student data.

### JWT session handling

Custom serializers in [steam_api/serializers/custom_token_obtain_pair_serializer.py](steam_api/serializers/custom_token_obtain_pair_serializer.py) and `custom_token_refresh_serializer.py` override SimpleJWT to (1) write a Redis session entry on token issue/refresh, (2) embed `user_info` in the token response, and (3) translate auth failures into `UnVerifiedException` / `PermissionDenied` so the view can branch on account status (`unverified` triggers an OTP email, `blocked` returns 403).

`custom_user_authentication_rule` ([steam_api/middlewares/custom_user_authentication_rule.py](steam_api/middlewares/custom_user_authentication_rule.py)) gates token issuance on `status == ACTIVATED`.

### Response wrapper

All views return responses via [`RestResponse`](steam_api/helpers/response.py) — a thin wrapper around DRF's `Response` that always emits `{data, code, message}` and provides Vietnamese default messages for common HTTP statuses. Don't return raw `Response` objects; mirror the existing pattern.

### Soft delete

Models use a `deleted_at: DateTimeField(null=True)` column rather than hard deletes. Always filter `deleted_at__isnull=True` in queries, and on `destroy` set `deleted_at = timezone.now()` and `is_active = False` (see [steam_api/views/web/course.py:188-200](steam_api/views/web/course.py#L188-L200)).

### Storage

Image/file uploads go to **Google Drive** via [steam_api/helpers/google_drive_storage.py](steam_api/helpers/google_drive_storage.py), not Django's `MEDIA_ROOT`. The helper uploads to `GDRIVE_DEFAULT_FOLDER_ID`, makes the file public, and returns `webViewLink`. Requires a service account JSON at `GDRIVE_SERVICE_ACCOUNT_FILE`. Live callers are the image-bearing serializers (`course`, `student`, `facility_image`, `lesson_gallery`) and [steam_api/views/web/news.py](steam_api/views/web/news.py).

`helpers/firebase_storage.py` and `helpers/local_storage.py` exist but are **unused** — nothing in `views/`, `serializers/`, or `models/` imports them (and `firebase_admin` sits in `requirements.txt` while being imported nowhere). Treat them as legacy; Google Drive is the only live backend.

### Caching / OTP

Redis is used both as Django's cache backend and as the session store. OTPs (account verification) live in Redis with key pattern `{purpose}:account:{email}:otp:{otp}` and a 1h TTL — see [steam_api/helpers/otp.py](steam_api/helpers/otp.py).

### Domain constants & lesson scheduling

- **Evaluation rubric** — the per-lesson student scoring criteria live as a single source of truth in [steam_api/const/score_criteria.py](steam_api/const/score_criteria.py) (`SCORE_CRITERIA`): each entry has a Vietnamese `name`, a machine `code` (`focus_score`, `punctuality_score`, `interaction_score`, `project_idea_score`, …), and a 1–5 `options` scale. `EvaluationCriteriaView` serves this list verbatim, and `lesson_evaluation` stores scores against these `code`s. When changing the rubric, edit this constant — don't hard-code criteria in views/serializers.
- **Lesson date computation** — [steam_api/helpers/lesson_schedule.py](steam_api/helpers/lesson_schedule.py) (`get_lesson_date`) derives a concrete lesson date from a class's weekly `schedule` dict (e.g. `{"monday": "...", "wednesday": "..."}`) plus a 1-based `lesson_sequence`. It's consumed by [steam_api/models/lesson.py](steam_api/models/lesson.py); reuse it rather than re-deriving dates.
- **Other constants** — `const/const.py` holds `ZALO_USER_INFO_API` (the Zalo Graph endpoint app auth calls). `errors/un_verified_exception.py` defines `UnVerifiedException`, raised by the custom token serializers to signal an unverified account.

### MySQL via PyMySQL

[steam/__init__.py](steam/__init__.py) calls `pymysql.install_as_MySQLdb()` so Django's `mysql` engine works without compiling `mysqlclient`. Don't remove this — it runs before Django imports the DB driver.

### Logging

Production logs go to BetterStack (Logtail) via the `logtail` handler configured in [steam/settings.py:207-229](steam/settings.py#L207-L229). The convention throughout the codebase is `logging.getLogger().info("ClassName.method ...", args)` — match this style. Note `disable_existing_loggers: True` silences Django's default loggers.

## Conventions when adding a feature

A typical resource (e.g. "widget") spans these files — follow the existing layout rather than introducing new patterns:

1. `steam_api/models/widget.py` — model with `created_at`, `updated_at`, `deleted_at`, `is_active`, explicit `db_table` in `Meta`.
2. `steam_api/serializers/widget.py` — separate serializers for read (`WidgetSerializer`), `Create...`, `Update...`. Validation lives here.
3. `steam_api/views/web/widget.py` and/or `steam_api/views/app/widget.py` — `viewsets.ViewSet` (not `ModelViewSet`), explicit `list/retrieve/create/update/destroy` methods, each wrapped in try/except returning `RestResponse`, with `@swagger_auto_schema` decorators.
4. Register in [steam_api/urls.py](steam_api/urls.py) under the appropriate router.
5. `python manage.py makemigrations && migrate`.

## Environment

Required `.env` keys (see [steam/settings.py](steam/settings.py) for usage):
`DATABASE_ENGINE/NAME/USER/PASSWORD/HOST/PORT`, `REDIS_HOST/PORT/USERNAME/PASSWORD`, `EMAIL_HOST/PORT/HOST_USER/HOST_PASSWORD`, `BETTERSTACK_LOG_TOKEN/HOST`, `GDRIVE_SERVICE_ACCOUNT_FILE`, `GDRIVE_DEFAULT_FOLDER_ID`.

The `.env` and `service_account.json.gpg` in this repo contain real credentials — treat as secrets, never log or commit changes that expose them.

## Reference docs in repo

[README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), [API_DOCUMENTATION.md](API_DOCUMENTATION.md), [DEPLOYMENT.md](DEPLOYMENT.md), [QUICK_START.md](QUICK_START.md) are extensive Vietnamese-language docs. They cover business domain (course/lesson/attendance/evaluation flows, the 12 evaluation criteria) more deeply than the code comments do — consult them when changing domain logic.
