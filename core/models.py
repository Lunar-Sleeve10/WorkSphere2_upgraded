from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    is_freelancer = models.BooleanField('Is freelancer', default=False)
    is_recruiter = models.BooleanField('Is recruiter', default=False)

    def __str__(self):
        return self.username

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.name
    
    class Meta:
        ordering =['name']

class FreelancerData(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key = True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # --- ADDED FIELDS START ---
    email = models.EmailField(max_length=254, blank=True)
    linkedin_url = models.URLField(max_length=200, blank=True)
    # --- ADDED FIELDS END ---
    phone_number = models.CharField(max_length=25)
    profile_summary = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    experience_years = models.IntegerField()
    expected_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='freelancers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Freelancer Profile"


class RecruiterData(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key = True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25)
    profile_summary = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    experience_years = models.IntegerField()
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Recruiter Profile"




class Job(models.Model):
    rate_type_choices = [
        ('HOURLY', 'Hourly'),
        ('FIXED', 'Fixed Project')
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, help_text="Location or mention remote")
    recruiter = models.ForeignKey(RecruiterData, on_delete=models.CASCADE, related_name='jobs')
    required_skills = models.ManyToManyField(Skill, related_name='jobs_requiring', help_text='Required Skills', blank=True)

    rate_type = models.CharField(
        max_length=10,
        choices=rate_type_choices,
        default='HOURLY',
        help_text="Type of compensation (e.g., Hourly, Fixed)."
    )
    rate_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text='Hourly rate or fixed project cost'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Job status"
    )
    posted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the job was originally posted"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the job was last updated."
    )

    def __str__(self):
        return f"{self.title} by {self.recruiter.company_name}"

    class Meta:
        ordering = ['-posted_at']



class Application(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ACCEPTED','Accepted'),
        ('DECLINED','Declined'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    freelancer = models.ForeignKey(
        FreelancerData,
        on_delete= models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=10,
        choices = STATUS_CHOICES,
        default='PENDING'
    )
    cover_letter = models.TextField(
        blank=True,
        null= True,
        help_text="optional"
    )
    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        job_title = self.job.title if self.job else "[Deleted Job]"
        freelancer_name = self.freelancer.user.username if self.freelancer and hasattr(self.freelancer, 'user') else "[Deleted Freelancer]"
        return f"Application by {freelancer_name} for {job_title}"

    class Meta:
        unique_together = ('job','freelancer')
        ordering = ['-applied_at']