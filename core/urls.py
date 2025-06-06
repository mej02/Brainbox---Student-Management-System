from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, SubjectViewSet, GradeViewSet, RegisterView, LoginView, EnrollmentViewSet, StudentEnrollmentsAPIView, EnrollSubjectAPIView, UnenrollSubjectAPIView
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@ensure_csrf_cookie
@api_view(["GET"])
@permission_classes([AllowAny])
def get_csrf_token(request):
    return Response({"detail": "CSRF cookie set"})




router = DefaultRouter()
router.register(r'students', StudentViewSet) # /api/students/, /api/students/{student_id}/
router.register(r'subjects', SubjectViewSet) # /api/subjects/, /api/subjects/{code}/
router.register(r'grades', GradeViewSet)     # /api/grades/, /api/grades/{id}/
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'), 
    path('login/', LoginView.as_view(), name='login'),       
    path('csrf/', get_csrf_token, name='csrf'),  
    path('students/<str:student_id>/enrollments/', StudentEnrollmentsAPIView.as_view(), name='student-enrollments'),
    path('students/<str:student_id>/enroll/', EnrollSubjectAPIView.as_view(), name='student-enroll'),
    path('students/<str:student_id>/unenroll/', UnenrollSubjectAPIView.as_view(), name='student-unenroll'),
]
