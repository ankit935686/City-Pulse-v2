#!/usr/bin/env python
"""
Django script to populate complaint data with 25 complaints from different users and locations.
Run this script from the project directory: python populate_complaints.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Complaint, UserProfile
from django.core.files.base import ContentFile
from PIL import Image
import io

def create_sample_image():
    """Create a simple sample image for complaints"""
    # Create a simple 100x100 image with a solid color
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return ContentFile(img_io.getvalue(), name='sample_complaint.jpg')

def populate_complaints():
    """Populate the database with 25 sample complaints"""
    
    # Sample users data
    users_data = [
        {'username': 'mumbai_citizen_1', 'email': 'citizen1@example.com', 'first_name': 'Rajesh', 'last_name': 'Patel'},
        {'username': 'mumbai_citizen_2', 'email': 'citizen2@example.com', 'first_name': 'Priya', 'last_name': 'Sharma'},
        {'username': 'mumbai_citizen_3', 'email': 'citizen3@example.com', 'first_name': 'Amit', 'last_name': 'Kumar'},
        {'username': 'mumbai_citizen_4', 'email': 'citizen4@example.com', 'first_name': 'Neha', 'last_name': 'Singh'},
        {'username': 'mumbai_citizen_5', 'email': 'citizen5@example.com', 'first_name': 'Suresh', 'last_name': 'Verma'},
        {'username': 'mumbai_citizen_6', 'email': 'citizen6@example.com', 'first_name': 'Anjali', 'last_name': 'Gupta'},
        {'username': 'mumbai_citizen_7', 'email': 'citizen7@example.com', 'first_name': 'Vikram', 'last_name': 'Joshi'},
        {'username': 'mumbai_citizen_8', 'email': 'citizen8@example.com', 'first_name': 'Meera', 'last_name': 'Reddy'},
        {'username': 'mumbai_citizen_9', 'email': 'citizen9@example.com', 'first_name': 'Arun', 'last_name': 'Malhotra'},
        {'username': 'mumbai_citizen_10', 'email': 'citizen10@example.com', 'first_name': 'Kavita', 'last_name': 'Iyer'},
    ]
    
    # Mumbai locations with coordinates (latitude, longitude)
    mumbai_locations = [
        (19.0760, 72.8777),   # Mumbai City Center
        (19.2183, 72.9781),   # Andheri
        (19.0170, 72.8478),   # Bandra
        (19.0596, 72.8295),   # Santa Cruz
        (19.1136, 72.8697),   # Juhu
        (19.0760, 72.8777),   # Colaba
        (19.0170, 72.8478),   # Worli
        (19.0596, 72.8295),   # Dadar
        (19.1136, 72.8697),   # Mahim
        (19.0760, 72.8777),   # Parel
        (19.0170, 72.8478),   # Sewri
        (19.0596, 72.8295),   # Wadala
        (19.1136, 72.8697),   # Sion
        (19.0760, 72.8777),   # Kurla
        (19.0170, 72.8478),   # Ghatkopar
        (19.0596, 72.8295),   # Vikhroli
        (19.1136, 72.8697),   # Kanjurmarg
        (19.0760, 72.8777),   # Bhandup
        (19.0170, 72.8478),   # Mulund
        (19.0596, 72.8295),   # Thane
        (19.1136, 72.8697),   # Navi Mumbai
        (19.0760, 72.8777),   # Chembur
        (19.0170, 72.8478),   # Govandi
        (19.0596, 72.8295),   # Mankhurd
    ]
    
    # Complaint types and their descriptions
    complaint_types_data = [
        ('POTHOLE', [
            'Large pothole on main road causing traffic',
            'Deep pothole near bus stop',
            'Multiple potholes on residential street',
            'Pothole filled with water after rain',
            'Dangerous pothole on highway'
        ]),
        ('WATER_LEAK', [
            'Water pipeline burst on street',
            'Leaking water main causing flooding',
            'Broken water hydrant',
            'Water leak from underground pipe',
            'Sewage water overflow'
        ]),
        ('BROKEN_SIGNAL', [
            'Traffic signal not working',
            'Faulty pedestrian crossing signal',
            'Broken traffic light at intersection',
            'Signal timing issue causing congestion',
            'Non-functional traffic signal'
        ]),
        ('GARBAGE', [
            'Garbage not collected for days',
            'Overflowing garbage bins',
            'Illegal garbage dumping',
            'Stray animals near garbage area',
            'Unhygienic garbage disposal'
        ]),
        ('OTHER', [
            'Broken street light',
            'Damaged road divider',
            'Missing manhole cover',
            'Overgrown trees blocking road',
            'Damaged public bench'
        ])
    ]
    
    # Create users if they don't exist
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created user: {user.username}")
        
        # Create UserProfile if it doesn't exist
        profile, profile_created = UserProfile.objects.get_or_create(user=user)
        if profile_created:
            print(f"Created profile for user: {user.username}")
        
        users.append(user)
    
    # Create sample image
    sample_image = create_sample_image()
    
    # Create 25 complaints
    complaints_created = 0
    statuses = ['PENDING', 'IN_PROGRESS', 'RESOLVED']
    
    for i in range(25):
        # Select random user and location
        user = random.choice(users)
        location = random.choice(mumbai_locations)
        
        # Add some random variation to coordinates
        lat = location[0] + random.uniform(-0.01, 0.01)
        lng = location[1] + random.uniform(-0.01, 0.01)
        
        # Select random complaint type and description
        complaint_type, descriptions = random.choice(complaint_types_data)
        description = random.choice(descriptions)
        
        # Create title based on complaint type
        titles = {
            'POTHOLE': f'Pothole Issue at {user.first_name}\'s Area',
            'WATER_LEAK': f'Water Leak Problem in {user.first_name}\'s Neighborhood',
            'BROKEN_SIGNAL': f'Traffic Signal Issue near {user.first_name}\'s Location',
            'GARBAGE': f'Garbage Collection Problem in {user.first_name}\'s Area',
            'OTHER': f'Infrastructure Issue in {user.first_name}\'s Community'
        }
        
        title = titles[complaint_type]
        
        # Random status with weighted probability (more pending than resolved)
        status_weights = {'PENDING': 0.5, 'IN_PROGRESS': 0.3, 'RESOLVED': 0.2}
        status = random.choices(statuses, weights=[status_weights[s] for s in statuses])[0]
        
        # Random creation date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Create complaint
        complaint = Complaint.objects.create(
            user=user,
            title=title,
            description=description,
            image=sample_image,
            complaint_type=complaint_type,
            latitude=lat,
            longitude=lng,
            status=status,
            created_at=created_at
        )
        
        complaints_created += 1
        print(f"Created complaint {complaints_created}: {complaint_type} by {user.username} at ({lat:.4f}, {lng:.4f})")
    
    print(f"\nSuccessfully created {complaints_created} complaints!")
    print(f"Total complaints in database: {Complaint.objects.count()}")
    print(f"Total users in database: {User.objects.count()}")

if __name__ == '__main__':
    print("Starting complaint population script...")
    populate_complaints()
    print("Complaint population completed!")
