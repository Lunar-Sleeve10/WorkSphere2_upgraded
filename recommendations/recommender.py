# In recommendations/recommender.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.models import Job, FreelancerData, Application

def get_job_recommendations(freelancer):
    """
    Recommends jobs for a given freelancer based on their skills and profile summary.
    """
    # Combine freelancer's skills and profile summary into a single string
    freelancer_profile_text = ' '.join([skill.name for skill in freelancer.skills.all()]) + ' ' + freelancer.profile_summary

    # Get all active jobs that have not been filled
    active_jobs = Job.objects.filter(is_active=True).exclude(applications__status='ACCEPTED')
    if not active_jobs.exists():
        return []

    # Create a list of job descriptions and their IDs
    job_texts = []
    job_ids = []
    for job in active_jobs:
        job_text = job.title + ' ' + job.description + ' ' + ' '.join([skill.name for skill in job.required_skills.all()])
        job_texts.append(job_text)
        job_ids.append(job.id)

    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    job_matrix = vectorizer.fit_transform(job_texts)

    # Transform the freelancer's profile text
    freelancer_vector = vectorizer.transform([freelancer_profile_text])

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(freelancer_vector, job_matrix).flatten()

    # Get the indices of the top 5 most similar jobs
    top_job_indices = cosine_similarities.argsort()[-5:][::-1]

    # Get the recommended job IDs
    recommended_job_ids = [job_ids[i] for i in top_job_indices]

    # Return the recommended Job objects
    recommended_jobs = Job.objects.filter(id__in=recommended_job_ids)
    return recommended_jobs

def rank_applications(job):
    """
    Ranks applicants for a given job based on skill and profile similarity.
    """
    job_text = job.title + ' ' + job.description + ' ' + ' '.join([skill.name for skill in job.required_skills.all()])
    applications = Application.objects.filter(job=job).select_related('freelancer')

    if not applications.exists():
        return []

    applicant_profiles = []
    for app in applications:
        freelancer_text = ' '.join([skill.name for skill in app.freelancer.skills.all()]) + ' ' + app.freelancer.profile_summary
        applicant_profiles.append(freelancer_text)

    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    applicant_matrix = vectorizer.fit_transform(applicant_profiles)

    # Transform the job description
    job_vector = vectorizer.transform([job_text])

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(job_vector, applicant_matrix).flatten()

    # Add the score to each application object
    for i, app in enumerate(applications):
        app.match_score = cosine_similarities[i]

    # Sort applications by the match score in descending order
    ranked_applications = sorted(applications, key=lambda app: app.match_score, reverse=True)

    return ranked_applications

def get_resume_ats_score(job_text, resume_text):
    """
    Calculates the cosine similarity score between a job's text content
    and a resume's text content.
    """
    if not job_text or not resume_text:
        return 0

    # The documents to be compared
    documents = [job_text, resume_text]

    # Create the TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Calculate the cosine similarity between the first (job) and second (resume) document
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    # The result is a 2D array, so we return the single value
    return cosine_sim[0][0]