from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, SubjectViewSet, GradeViewSet, RegisterView, LoginView, EnrollmentViewSet, StudentEnrollmentsAPIView, EnrollSubjectAPIView, UnenrollSubjectAPIView
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .views import CsrfTokenView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

print("=== core/urls.py loaded ===")




router = DefaultRouter()
router.register(r'students', StudentViewSet) # /api/students/, /api/students/{student_id}/
router.register(r'subjects', SubjectViewSet) # /api/subjects/, /api/subjects/{code}/
router.register(r'grades', GradeViewSet)     # /api/grades/, /api/grades/{id}/
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'), 
    path('login/', LoginView.as_view(), name='login'),       
    path('csrf/', CsrfTokenView.as_view(), name='csrf'),
    path('api/students/<str:student_id>/enrollments/', StudentEnrollmentsAPIView.as_view(), name='student-enrollments'),
    path('api/students/<str:student_id>/enroll/', EnrollSubjectAPIView.as_view(), name='student-enroll'),
    path('api/students/<str:student_id>/unenroll/', UnenrollSubjectAPIView.as_view(), name='student-unenroll'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

