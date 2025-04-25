# create_profiles.py
# Run this with: python manage.py shell < create_profiles.py

from django.contrib.auth.models import User
from foundapp.models import UserProfile

# Create profiles for users that don't have one
for user in User.objects.all():
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'user'})

print(f"Created profiles for users!")