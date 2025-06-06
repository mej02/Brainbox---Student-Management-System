from rest_framework import serializers
from .models import Student, Subject, Grade, Enrollment
from django.contrib.auth.models import User

class StudentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'student_id', 'first_name', 'last_name', 'gender', 'date_of_birth',
            'email', 'section', 'course', 'year_level', 'image', 'image_url',
            'contact_number', 'address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['image_url', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:

            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url 
        return None    
    
    # --- Subject Serializer ---
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        # 'code' is the primary key, so it's implicitly handled.
        fields = ['code', 'name', 'units', 'description', 'created_at', 'updated_at']
        # Fields that should not be set by the client
        read_only_fields = ['created_at', 'updated_at']
    
 # --- Grade Serializer ---
class GradeSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    subject_details = SubjectSerializer(source='subject', read_only=True)
    final_grade = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'subject', 'activity_grade', 'quiz_grade', 'exam_grade',
            'final_grade', 'student_details', 'subject_details'
        ]
        read_only_fields = ['id', 'final_grade', 'student_details', 'subject_details']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Grade.objects.all(),
                fields=['student', 'subject'],
                message="A grade for this student and subject already exists."
            )
        ]   

         # Custom validation for grade components (0-100 range)
    def validate(self, data):
        for field in ['activity_grade', 'quiz_grade', 'exam_grade']:
            grade = data.get(field)
            if grade is not None and not (0 <= grade <= 100):
                raise serializers.ValidationError({field: "Grade must be between 0 and 100."})
        return data

# --- User Serializer for Registration ---
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) 

    class Meta:
        model = User
        fields = ['username', 'password']

    # Override create method to hash the password
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    
class EnrollmentSerializer(serializers.ModelSerializer):
    # These fields will embed the full student and subject details directly into the enrollment response
    student_details = StudentSerializer(source='student', read_only=True)
    subject_details = SubjectSerializer(source='subject', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'subject', 'enrollment_date',
            'student_details', 'subject_details'
        ]
        read_only_fields = ['id', 'enrollment_date', 'student_details', 'subject_details']

    # Custom validation to ensure 'student' and 'subject' are passed during creation/update
    def validate(self, data):
        # When creating or updating, ensure 'student' and 'subject' FKs are provided if not read-only
        if self.instance is None: # For create operation
            if 'student' not in data:
                raise serializers.ValidationError({"student": "This field is required."})
            if 'subject' not in data:
                raise serializers.ValidationError({"subject": "This field is required."})
        return data