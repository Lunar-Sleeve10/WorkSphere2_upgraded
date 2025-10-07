from django.urls import path
from .views import home, SignUpView, LoginView, logout_view, freelancer_dashboard, create_freelancer_profile ,recruiter_dashboard, recruiter_profile_edit,manage_job, recruited_job_list, job_list, job_detail,view_job_applications,update_application_status, apply_to_job, parse_resume_view , delete_account_view , remove_freelancer_skill,get_freelancer_ats_view

urlpatterns = [
    path('', home, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('freelancerdashboard/', freelancer_dashboard, name='freelancer_dashboard'),
    path('freelanceredit-profile/', create_freelancer_profile, name='edit_profile'),
    path('recruiter/profile/', recruiter_profile_edit, name='recruiter_profile_edit'),
    path('recruiter/dashboard/', recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/jobs/', recruited_job_list, name='recruiter_job_list'),
    path('jobs/create/', manage_job, name='create_job'),
    path('jobs/<int:job_id>/edit/', manage_job, name='edit_job'),
     path('jobs/', job_list, name='job_list'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    path('recruiter/jobs/<int:job_id>/applications/', view_job_applications, name='view_job_applications'),
    path('recruiter/applications/<int:application_id>/update/', update_application_status, name='update_application_status'),
    path('jobs/<int:job_id>/apply/', apply_to_job, name='apply_to_job'),
    path('profile/parse-resume/', parse_resume_view, name='parse_resume'),
    path('account/delete/', delete_account_view, name='delete_account'),
    path('profile/remove-skill' , remove_freelancer_skill , name='remove_freelancer_skill'),
    path('jobs/<int:job_id>/get-ats-score/', get_freelancer_ats_view, name='get_freelancer_ats'),
    
]

from django.conf import settings
from django.conf.urls.static import static



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)