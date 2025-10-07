import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.models import Job, FreelancerData, Application

def get_job_recommendations(freelancer):
    freelancer_profile_text = ' '.join([skill.name for skill in freelancer.skills.all()]) + ' ' + freelancer.profile_summary
    active_jobs = Job.objects.filter(is_active=True).exclude(applications__status='ACCEPTED')
    if not active_jobs.exists():
        return []

    job_texts = []
    job_ids = []
    for job in active_jobs:
        job_text = job.title + ' ' + job.description + ' ' + ' '.join([skill.name for skill in job.required_skills.all()])
        job_texts.append(job_text)
        job_ids.append(job.id)

    vectorizer = TfidfVectorizer(stop_words='english')
    job_matrix = vectorizer.fit_transform(job_texts)
    freelancer_vector = vectorizer.transform([freelancer_profile_text])
    cosine_similarities = cosine_similarity(freelancer_vector, job_matrix).flatten()
    top_job_indices = cosine_similarities.argsort()[-5:][::-1]
    recommended_job_ids = [job_ids[i] for i in top_job_indices]
    recommended_jobs = Job.objects.filter(id__in=recommended_job_ids)
    return recommended_jobs

def rank_applications(job):
    job_text = job.title + ' ' + job.description + ' ' + ' '.join([skill.name for skill in job.required_skills.all()])
    applications = Application.objects.filter(job=job).select_related('freelancer')
    if not applications.exists():
        return []

    applicant_profiles = []
    for app in applications:
        freelancer_text = ' '.join([skill.name for skill in app.freelancer.skills.all()]) + ' ' + app.freelancer.profile_summary
        applicant_profiles.append(freelancer_text)

    vectorizer = TfidfVectorizer(stop_words='english')
    applicant_matrix = vectorizer.fit_transform(applicant_profiles)
    job_vector = vectorizer.transform([job_text])
    cosine_similarities = cosine_similarity(job_vector, applicant_matrix).flatten()

    for i, app in enumerate(applications):
        app.match_score = cosine_similarities[i]

    ranked_applications = sorted(applications, key=lambda app: app.match_score, reverse=True)
    return ranked_applications

def get_resume_ats_score(job_text, resume_text):
    if not job_text or not resume_text:
        return 0

    documents = [job_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]
