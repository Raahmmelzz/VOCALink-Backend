from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, TeacherProfile, Board

# --- INLINES ---
# These allow you to edit the profile details directly on the User page
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'

# --- USER ADMIN ---
class CustomUserAdmin(UserAdmin):
    """
    Customizing the User Admin to show the profiles 
    and use our custom manager fields.
    """
    list_display = ('email', 'username', 'is_staff', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    # This determines which profile shows up in the admin based on what exists
    inlines = [StudentProfileInline, TeacherProfileInline]

# --- REGISTER MODELS ---

admin.site.register(User, CustomUserAdmin)
admin.site.register(Board)

# Registering profiles separately as well so you can view them in a list
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'user')
    search_fields = ('name', 'user__email')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'department', 'organization')
    search_fields = ('name', 'organization', 'user__email')