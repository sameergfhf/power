from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from foundapp.models import Item

class BidItem(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bid_items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_increment = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    image = models.FileField(upload_to='bid_items/', blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=7))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def time_remaining(self):
        if self.end_date and self.status == 'active':
            now = timezone.now()
            if now > self.end_date:
                return "Expired"
            delta = self.end_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            else:
                return f"{minutes}m {seconds}s"
        return "N/A"
    
    def highest_bidder(self):
        highest_bid = self.bids.order_by('-amount').first()
        if highest_bid:
            return highest_bid.user
        return None
    
    def bid_count(self):
        return self.bids.count()
    
    def has_ended(self):
        if not self.end_date:
            return False
        return timezone.now() > self.end_date
    
    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new instance
            self.current_price = self.initial_price
            if not self.end_date:
                self.end_date = timezone.now() + timezone.timedelta(days=7)
        
        if self.status == 'active' and not self.start_date:
            self.start_date = timezone.now()
        
        if self.pk is not None:
            orig = BidItem.objects.get(pk=self.pk)
            if orig.status != 'sold' and self.status == 'sold' and self.related_item:
                self.related_item.is_resolved = True
                self.related_item.save()
        
        super().save(*args, **kwargs)

class BidItemImage(models.Model):
    bid_item = models.ForeignKey(BidItem, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='bid_items/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.bid_item.title}"

class Bid(models.Model):
    bid_item = models.ForeignKey(BidItem, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} bid ${self.amount} on {self.bid_item.title}"
    
    class Meta:
        ordering = ['-amount']

class BidNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_bid', 'New Bid'),
        ('outbid', 'Outbid'),
        ('won', 'Won Auction'),
        ('ended', 'Auction Ended'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bid_notifications')
    bid_item = models.ForeignKey(BidItem, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']