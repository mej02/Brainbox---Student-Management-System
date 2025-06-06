from django.db import models
import datetime

COURSE_CHOICES = [
    ('BSIT', 'BSIT - Bachelor of Science in Information Technology'),
    ('BSCS', 'BSCS - Bachelor of Science in Computer Science'),
    ('BSCRIM', 'BSCRIM - Bachelor of Science in Criminology'),
    ('BSBM', 'BSBM - Bachelor of Science in Business Management'),
    ('BSED', 'BSED - Bachelor of Secondary Education'),
    ('BSHM', 'BSHM - Bachelor of Science in Hospitality Management'),
    ('BSP', 'BSP - Bachelor of Science in Psychology'),
]

YEAR_LEVEL_CHOICES = [
    ('1st Year', '1st Year'),
    ('2nd Year', '2nd Year'),
    ('3rd Year', '3rd Year'),
    ('4th Year', '4th Year'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

# --- Student Model ---
# Represents a student with their personal and academic details.
class Student(models.Model):
    
    student_id = models.CharField(max_length=20, unique=True, primary_key=True, help_text="Unique student identifier (e.g., 202212312)")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other') # Added Gender
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    section = models.IntegerField(help_text="Student's section (e.g., 1, 2, 3)") # Section as an Integer
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year_level = models.CharField(max_length=20, choices=YEAR_LEVEL_CHOICES)
    image = models.ImageField(upload_to='student_images/', null=True, blank=True, help_text="Profile picture of the student") # Image upload field
    contact_number = models.CharField(max_length=20, blank=True, null=True) # Added Contact Number
    address = models.TextField(blank=True, null=True) # Added Address

    # Timestamps for creation and last update
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default ordering for queries
        ordering = ['student_id']

    def __str__(self):
        # String representation for admin and debugging
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    

# --- Subject Model ---
class Subject(models.Model):
    # code as primary key for direct lookup and uniqueness
    code = models.CharField(max_length=20, unique=True, primary_key=True, help_text="Subject code (e.g., CS101)")
    name = models.CharField(max_length=100, unique=True, help_text="Full subject name (e.g., Computer Programming 1)")
    units = models.DecimalField(max_digits=3, decimal_places=1, help_text="Number of academic units/credits")
    description = models.TextField(blank=True, null=True, help_text="Brief description of the subject content") # Added description

    # Timestamps for creation and last update
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default ordering for queries
        ordering = ['code']

    def __str__(self):
        # String representation for admin and debugging
        return f"{self.code} - {self.name}"
    



# --- Grade Model ---
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')

    # Individual grade components
    activity_grade = models.DecimalField(max_digits=5, decimal_places=2, help_text="Grade for activities (0-100)")
    quiz_grade = models.DecimalField(max_digits=5, decimal_places=2, help_text="Grade for quizzes (0-100)")
    exam_grade = models.DecimalField(max_digits=5, decimal_places=2, help_text="Grade for exams (0-100)")

    class Meta:
        # Ensures that a student can only have one grade entry per subject
        unique_together = ('student', 'subject')
        # Default ordering for queries
        ordering = ['student', 'subject']

    def __str__(self):
        # String representation for admin and debugging
        return f"Grade for {self.student.student_id} in {self.subject.code}"
    
    @property
    def final_grade(self):
        return ((float(self.activity_grade) * 0.30) +
                (float(self.quiz_grade) * 0.30) +
                (float(self.exam_grade) * 0.40))
    
    

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True) # Automatically set when created

    class Meta:
        unique_together = ('student', 'subject') # Ensures a student can only enroll in a subject once
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} enrolled in {self.subject.name}"   