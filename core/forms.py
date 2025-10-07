# In core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, FreelancerData, Skill, RecruiterData, Job


class SignUpForm(UserCreationForm):
    type = forms.ChoiceField(choices = [('freelancer','Freelancer'),('recruiter','Recruiter')], required= True)
                                
    class Meta:
        model = User
        fields = ('username','password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data['type']
        if user_type == 'freelancer':
            user.is_freelancer = True
        elif user_type == 'recruiter':
            user.is_recruiter = True
        if commit:
            user.save()
        return user
    

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('email', 'password')



class FreelancerDataForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, React (comma-separated)'}),
        help_text="Enter skills separated by commas. Add new skills here."
    )

    class Meta:
        model = FreelancerData
        # --- ADDED FIELDS START ---
        fields = [
            'first_name',
            'last_name',
            'email',
            'linkedin_url',
            'phone_number',
            'profile_summary',
            'location',
            'experience_years',
            'expected_hourly_rate',
            'resume',
            'profile_picture',
            'skills',
        ]
        # --- ADDED FIELDS END ---
        widgets = {
            'profile_summary': forms.Textarea(attrs={'rows': 4}),
            # --- ADDED WIDGETS START ---
            'email': forms.EmailInput(attrs={'placeholder': 'e.g., your.email@example.com'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'e.g., https://www.linkedin.com/in/yourprofile'}),
            # --- ADDED WIDGETS END ---
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if instance and instance.pk:
            # Pre-fill skills as a comma-separated string for editing
            skill_names = [skill.name for skill in instance.skills.all()]
            self.fields['skills'].initial = ', '.join(skill_names)
        else:
            self.fields['skills'].initial = ''


    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # This custom save handles the string-based skills input
        if commit:
            instance.save()
            
            # Save the M2M relationship for skills from the text input
            submitted_skill_names_str = self.cleaned_data.get('skills', '')
            submitted_skill_names = {name.strip().lower() for name in submitted_skill_names_str.split(',') if name.strip()}
            
            # Clear existing skills and add the new set
            instance.skills.clear()
            for name in submitted_skill_names:
                skill_obj, created = Skill.objects.get_or_create(name=name)
                instance.skills.add(skill_obj)
        
        # This is required by Django's ModelForm save method convention
        self.save_m2m = lambda: None

        return instance



class RecruiterDataForm(forms.ModelForm):
    
    class Meta:
        model = RecruiterData

        fields = [
            'first_name',
            'last_name',
            'company_name',
            'phone_number',
            'profile_summary',
            'location',
            'experience_years',
            'profile_picture',
        ]
class JobPostForm(forms.ModelForm):

    required_skills = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, API Design (comma-separated)'}),
        label="Required Skills",
        help_text="Enter required skills "
    )

    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'location',
            'required_skills',
            'rate_type',
            'rate_amount',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the job responsibilities, requirements, etc.'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Noida, Uttar Pradesh or Remote'}),
            'rate_amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g., 500.00 or 25000.00'}),
        }
        labels = {
            'title': 'Job Title',
            'description': 'Job Description',
            'location': 'Location',
            'rate_type': 'Compensation Type',
            'rate_amount': 'Compensation Amount (₹)',
        }
        help_texts = {
            'rate_amount': 'Enter the amount based on the Compensation Type (e.g., hourly rate or total fixed project cost).',
        }


    def save(self, commit=True, recruiter=None):
        instance = super().save(commit=False)

        if recruiter:
            instance.recruiter = recruiter

        if commit:
            instance.save() 
            # Clear existing skills before adding new ones
            instance.required_skills.clear()

            submitted_skill_names_str = self.cleaned_data.get('required_skills', '')
            submitted_skill_names = {name.strip().lower() for name in submitted_skill_names_str.split(',') if name.strip()}

            skill_objs = set()
            for name in submitted_skill_names:
                if name:
                    skill_obj, created = Skill.objects.get_or_create(name=name) 
                    skill_objs.add(skill_obj)
            
            if skill_objs:
                instance.required_skills.add(*skill_objs) 

        return instance


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.pk:
            current_skills = instance.required_skills.order_by('name')
            initial_skills_string = ", ".join([skill.name for skill in current_skills])
            self.fields['required_skills'].initial = initial_skills_string