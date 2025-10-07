# In core/management/commands/seed_data.py

import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.hashers import make_password

from core.models import User, Skill, FreelancerData, RecruiterData, Job, Application

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Clean up old data
        User.objects.filter(is_superuser=False).delete()
        Skill.objects.all().delete()
        Job.objects.all().delete()

        fake = Faker()

        # --- Create Skills ---
        skills = ['Python', 'Django', 'JavaScript', 'React', 'Vue.js', 'SQL', 'PostgreSQL', 'Docker', 'AWS', 'HTML', 'CSS']
        skill_objects = [Skill.objects.create(name=skill_name.lower()) for skill_name in skills]
        self.stdout.write(f"Created {len(skill_objects)} skills.")

        # --- Create Freelancers ---
        freelancers = []
        for _ in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'{first_name.lower()}{last_name.lower()}'
            email = f'{username}@example.com'
            
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password('password123'),
                is_freelancer=True
            )
            
            freelancer_profile = FreelancerData.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone_number=fake.phone_number(),
                profile_summary=fake.paragraph(nb_sentences=5),
                location=fake.city(),
                experience_years=random.randint(1, 15),
                expected_hourly_rate=random.uniform(25.0, 150.0)
            )
            
            # Assign 3 to 5 random skills to the freelancer
            freelancer_profile.skills.set(random.sample(skill_objects, k=random.randint(3, 5)))
            freelancers.append(freelancer_profile)

        self.stdout.write(f"Created {len(freelancers)} freelancers.")

        # --- Create Recruiters ---
        recruiters = []
        for _ in range(5):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'recruiter_{first_name.lower()}'
            email = f'{username}@company.com'

            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password('password123'),
                is_recruiter=True
            )

            recruiter_profile = RecruiterData.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                company_name=fake.company(),
                phone_number=fake.phone_number(),
                profile_summary=fake.bs(),
                location=fake.city(),
                experience_years=random.randint(2, 20)
            )
            recruiters.append(recruiter_profile)
        
        self.stdout.write(f"Created {len(recruiters)} recruiters.")

        # --- Create Jobs ---
        jobs = []
        for _ in range(20):
            recruiter = random.choice(recruiters)
            job = Job.objects.create(
                recruiter=recruiter,
                title=fake.job(),
                description=fake.paragraph(nb_sentences=10),
                location=random.choice([recruiter.location, 'Remote']),
                rate_type=random.choice(['HOURLY', 'FIXED']),
                rate_amount=random.uniform(500.0, 50000.0)
            )
            # Assign 2 to 4 random skills to the job
            job.required_skills.set(random.sample(skill_objects, k=random.randint(2, 4)))
            jobs.append(job)

        self.stdout.write(f"Created {len(jobs)} jobs.")

        # --- Create Applications ---
        application_count = 0
        for job in jobs:
            # Each job gets 1 to 5 applications
            applicants = random.sample(freelancers, k=random.randint(1, 5))
            for freelancer in applicants:
                Application.objects.create(
                    job=job,
                    freelancer=freelancer,
                    cover_letter=fake.paragraph(nb_sentences=3)
                )
                application_count += 1
        
        self.stdout.write(f"Created {application_count} applications.")
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))