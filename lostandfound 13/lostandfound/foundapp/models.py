from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.FileField(upload_to='profile_images/', default='profile_images/default.png')
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile - {self.role}"


# Create UserProfile automatically when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            UserProfile.objects.create(user=instance, role='admin')  # Create admin profile for superuser
        else:
            UserProfile.objects.create(user=instance)  # Create regular user profile


# Save UserProfile when User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Only update profile if it exists, otherwise it will be created by the create_user_profile signal
    if hasattr(instance, 'profile'):
        instance.profile.save()



class UserQuestion(models.Model):
    question = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)  # Added reply field

    def __str__(self):
        return self.question[:50]
    


class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
    ]
    
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('jewelry', 'Jewelry'),
        ('clothing', 'Clothing'),
        ('documents', 'Documents'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')

    item_type = models.CharField(max_length=5, choices=ITEM_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    date_lost_found = models.DateField()
    time_lost_found = models.TimeField(null=True, blank=True)
    description = models.TextField()
    image = models.FileField(upload_to='items/', null=True, blank=True)
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    preferred_contact = models.CharField(max_length=10, default='email')
    additional_notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_item_type_display()} - {self.name}"
    
    class Meta:
        ordering = ['-date_created']

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='items/')
    
    def __str__(self):
        return f"Image for {self.item.name}"
    

    class AdminRequest(models.Model):
        STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ]
    
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_requests')
        reason = models.TextField()
        status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
    
        def   __str__(self):
            return f"{self.user.username}'s admin request - {self.status}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s bid on {self.item.name} - ${self.amount}"
    

    # Add these new models to your models.py file

class AdminRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_requests')
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s admin request - {self.status}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s bid on {self.item.name} - ${self.amount}"
    
# Add this to your existing models.py file

class AdminTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_tasks')
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['due_date', 'created_at']



# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ItemClaim(models.Model):
    CLAIM_TYPE_CHOICES = [
        ('found', 'Found Item'),
        ('ownership', 'Ownership Claim'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='claims')
    claim_type = models.CharField(max_length=10, choices=CLAIM_TYPE_CHOICES)
    claimer_name = models.CharField(max_length=100)
    claimer_email = models.EmailField()
    claimer_phone = models.CharField(max_length=20)
    
    # For found items
    found_location = models.CharField(max_length=255, blank=True, null=True)
    found_date = models.DateField(blank=True, null=True)
    found_description = models.TextField(blank=True, null=True)
    
    # For ownership claims
    ownership_proof = models.TextField(blank=True, null=True)
    
    # Common fields
    image = models.FileField(upload_to='claim_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User if authenticated
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Reviewed info
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewer_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.claim_type} claim for {self.item.name} by {self.claimer_name}"
    
    def approve(self, notes=None):
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        if notes:
            self.reviewer_notes = notes
        self.save()
    
    def reject(self, notes=None):
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        if notes:
            self.reviewer_notes = notes
        self.save()