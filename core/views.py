from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Student, Subject, Grade, Enrollment
from .serializers import StudentSerializer, SubjectSerializer, GradeSerializer, UserSerializer, EnrollmentSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import BasePermission

@ensure_csrf_cookie
def csrf(request):
    token = request.META.get("CSRF_COOKIE", "")
    return JsonResponse({"csrftoken": token})

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

# --- Student ViewSet ---
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'
    permission_classes = [IsTeacher]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class StudentEnrollmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        # You may want to check permissions here!
        enrollments = Enrollment.objects.filter(student__student_id=student_id)
        # Return just subject codes, or serialize as needed
        subject_codes = [e.subject.code for e in enrollments]
        return Response(subject_codes)



# --- Subject ViewSet ---
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    lookup_field = 'code' 

# --- Grade ViewSet ---
class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def create(self, request, *args, **kwargs):
        student_id = request.data.get('student') 
        subject_code = request.data.get('subject') 

        try:
            student_obj = Student.objects.get(student_id=student_id)
            subject_obj = Subject.objects.get(code=subject_code)
        except Student.DoesNotExist:
            return Response({"student": "Student with this ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Subject.DoesNotExist:
            return Response({"subject": "Subject with this code does not exist."}, status=status.HTTP_400_BAD_REQUEST)

       
        data = request.data.copy()
        data['student'] = student_obj.pk 
        data['subject'] = subject_obj.pk 

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) 
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False) 
        instance = self.get_object() 
        data = request.data.copy()

        # If student_id is provided in the update request, retrieve the Student object
        if 'student' in data:
            try:
                student_obj = Student.objects.get(student_id=data['student'])
                data['student'] = student_obj.pk 
            except Student.DoesNotExist:
                return Response({"student": "Student with this ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'subject' in data:
            try:
                subject_obj = Subject.objects.get(code=data['subject'])
                data['subject'] = subject_obj.pk 
            except Subject.DoesNotExist:
                return Response({"subject": "Subject with this code does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)    
    
# --- User Registration View ---
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')
        student_id = request.data.get('student_id')

        if not username or not password or not role:
            return Response({"message": "Username, password, and role are required."}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'student':
            if not student_id:
                return Response({"message": "Student ID is required for student registration."}, status=status.HTTP_400_BAD_REQUEST)
            # If a User already exists for this student_id, block registration
            if User.objects.filter(username=student_id).exists():
                return Response({"message": "A user with this student ID already exists."}, status=status.HTTP_400_BAD_REQUEST)
            # If Student exists but User does not, allow registration (do NOT create a new Student)
            if Student.objects.filter(student_id=student_id).exists():
                User.objects.create_user(username=student_id, password=password)
                return Response({"message": "Account created. You can now log in.", "role": "student", "student_id": student_id}, status=status.HTTP_201_CREATED)
            # If Student does not exist, create both Student and User
            user = User.objects.create_user(username=student_id, password=password)
            student_profile = Student.objects.create(
                student_id=student_id,
                first_name=username,  # or get from form
                last_name="User",
                email=f"{student_id}@example.com",
                date_of_birth='2000-01-01',
                section=1,
                course='BSIT',
                year_level='1st Year',
            )
            return Response({"message": "Student registered successfully.", "role": "student", "student_id": student_id}, status=status.HTTP_201_CREATED)
        else:
            if User.objects.filter(username=username).exists():
                return Response({"message": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(username=username, password=password)
            return Response({"message": "Teacher registered successfully.", "role": "teacher"}, status=status.HTTP_201_CREATED)

# --- User Login View ---
# Handles user authentication and returns role and student_id (if student).
class LoginView(APIView):
    @ensure_csrf_cookie
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"success": True})
        return Response({"success": False, "error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)    
        

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated] # Ensures only authenticated users can access enrollments

    # Optionally, to allow users to only see/manage their own enrollments
    def get_queryset(self):
        queryset = super().get_queryset()
        # If the user is a student, filter to show only their enrollments
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            # Assuming your User model has a one-to-one link to a StudentProfile or Student model
            # You might need to adjust 'student_profile' or 'student' based on your actual User-Student link
            # For example, if your User model *is* the Student model, it's just 'self.request.user'
            # If User has a ForeignKey to Student (or Student has a OneToOneField to User)
            # Find the student_id associated with the logged-in user
            student_id_from_user = None
            if hasattr(self.request.user, 'student') and self.request.user.student: # If User has a one-to-one with Student
                student_id_from_user = self.request.user.student.student_id
            elif self.request.user.username: # Fallback: if username is student_id
                student_id_from_user = self.request.user.username # Assuming username is student_id

            if student_id_from_user:
                 return queryset.filter(student__student_id=student_id_from_user)
            # If no student_id found for the logged-in user, return empty queryset
            return queryset.none()
        # If not authenticated, or not a student, return all (or none depending on desired behavior for others)
        # For authenticated users who are NOT students (e.g., teachers), they might see all enrollments
        return queryset # Teachers can see all enrollments

    # Allow a student to only create enrollments for themselves (optional, but good security)
    def perform_create(self, serializer):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student') and self.request.user.student:
            if serializer.validated_data['student'] != self.request.user.student:
                raise serializers.ValidationError("Students can only enroll themselves in subjects.")
        elif self.request.user.is_authenticated and self.request.user.username: # Fallback if username is student_id
             if serializer.validated_data['student'].student_id != self.request.user.username:
                 raise serializers.ValidationError("Students can only enroll themselves in subjects.")
        serializer.save()

class EnrollSubjectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        subject_code = request.data.get('subject_code')
        if not subject_code:
            return Response({'message': 'Subject code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(student_id=student_id)
            subject = Subject.objects.get(code=subject_code)
            # Prevent duplicate enrollments
            if Enrollment.objects.filter(student=student, subject=subject).exists():
                return Response({'message': 'Already enrolled in this subject.'}, status=status.HTTP_400_BAD_REQUEST)
            Enrollment.objects.create(student=student, subject=subject)
            return Response({'message': 'Enrolled successfully.'}, status=status.HTTP_201_CREATED)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Subject.DoesNotExist:
            return Response({'message': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)

class UnenrollSubjectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        subject_code = request.data.get('subject_code')
        if not subject_code:
            return Response({'message': 'Subject code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(student_id=student_id)
            subject = Subject.objects.get(code=subject_code)
            enrollment = Enrollment.objects.filter(student=student, subject=subject)
            if not enrollment.exists():
                return Response({'message': 'Not enrolled in this subject.'}, status=status.HTTP_400_BAD_REQUEST)
            enrollment.delete()
            return Response({'message': 'Unenrolled successfully.'}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Subject.DoesNotExist:
            return Response({'message': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)
