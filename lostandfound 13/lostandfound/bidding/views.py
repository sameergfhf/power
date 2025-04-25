from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Max, Count
from django.http import JsonResponse, FileResponse, Http404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import os
from .models import BidItem, Bid, BidItemImage, BidNotification
from .forms import BidItemForm, PlaceBidForm, BidItemImageForm
from .models import Item 

@login_required
def bidding_home(request):
    active_items = BidItem.objects.filter(status='active').order_by('-end_date')[:8]
    ending_soon = BidItem.objects.filter(
        status='active', 
        end_date__gt=timezone.now()
    ).order_by('end_date')[:4]
    
    popular_items = BidItem.objects.filter(status='active').annotate(
        bid_count=Count('bids')
    ).order_by('-bid_count')[:4]

    item_bid_forms = {}
    if request.user.is_authenticated:
        for item in list(active_items) + list(ending_soon) + list(popular_items):
            if item.id not in item_bid_forms:
                item_bid_forms[item.id] = PlaceBidForm(bid_item=item)
    
    context = {
        'active_items': active_items,
        'ending_soon': ending_soon,
        'popular_items': popular_items,
        'item_bid_forms': item_bid_forms,
    }
    return render(request, 'bidding/home.html', context)

class BidItemListView(ListView):
    model = BidItem
    template_name = 'bidding/bid_item_list.html'
    context_object_name = 'bid_items'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = BidItem.objects.filter(status='active')
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        sort_by = self.request.GET.get('sort_by', 'end_date')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('current_price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-current_price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'popularity':
            queryset = queryset.annotate(
                bid_count=Count('bids')
            ).order_by('-bid_count')
        else:
            queryset = queryset.order_by('end_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'end_date')
        return context

class BidItemDetailView(DetailView):
    model = BidItem
    template_name = 'bidding/bid_item_detail.html'
    context_object_name = 'bid_item'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bid_item = self.get_object()
        
        if bid_item.status == 'active' and not bid_item.has_ended():
            context['bid_form'] = PlaceBidForm(bid_item=bid_item)
        
        context['bid_history'] = bid_item.bids.all()[:10]
        
        if self.request.user.is_authenticated:
            BidNotification.objects.filter(
                user=self.request.user,
                bid_item=bid_item,
                is_read=False
            ).update(is_read=True)
        
        return context

@login_required
def add_bid_item(request):
    if request.method == 'POST':
        form = BidItemForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            bid_item = form.save(commit=False)
            bid_item.user = request.user
            bid_item.current_price = bid_item.initial_price
            bid_item.status = 'active'
            bid_item.start_date = timezone.now()
            bid_item.save()
            
            images = request.FILES.getlist('image')
            for image in images:
                BidItemImage.objects.create(bid_item=bid_item, image=image)
            
            messages.success(request, 'Your item has been listed successfully.')
            return redirect('my_bid_items')
    else:
        form = BidItemForm(user=request.user)
        image_form = BidItemImageForm()
    
    context = {
        'form': form,
        'image_form': image_form,
        'title': 'Add New Bid Item'
    }
    return render(request, 'bidding/bid_item_form.html', context)

@login_required
def place_bid(request, pk):
    bid_item = get_object_or_404(BidItem, pk=pk, status='active')
    
    if bid_item.has_ended():
        messages.error(request, "This auction has ended.")
        return redirect('bid_item_detail', pk=pk)
    
    if request.method == 'POST':
        form = PlaceBidForm(request.POST, bid_item=bid_item)
        
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            bid = Bid.objects.create(
                bid_item=bid_item,
                user=request.user,
                amount=amount
            )
            
            bid_item.current_price = amount
            bid_item.save()
            
            BidNotification.objects.create(
                user=bid_item.user,
                bid_item=bid_item,
                notification_type='new_bid',
                message=f"{request.user.username} placed a bid of ${amount} on your item '{bid_item.title}'."
            )
            
            previous_highest = bid_item.bids.exclude(id=bid.id).first()
            if previous_highest and previous_highest.user != request.user:
                BidNotification.objects.create(
                    user=previous_highest.user,
                    bid_item=bid_item,
                    notification_type='outbid',
                    message=f"You've been outbid on '{bid_item.title}'. The new highest bid is ${amount}."
                )
            
            messages.success(request, f"Your bid of ${amount} has been placed!")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'current_price': float(bid_item.current_price),
                    'message': f"Your bid of ${amount} has been placed!"
                })
            
            referer = request.META.get('HTTP_REFERER', '')
            if 'bidding_home' in referer or 'home' in referer:
                return redirect('bidding_home')
            
            return redirect('bid_item_detail', pk=pk)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            
            messages.error(request, "There was an error with your bid. Please check the form and try again.")
            
            referer = request.META.get('HTTP_REFERER', '')
            if 'bidding_home' in referer or 'home' in referer:
                return redirect('bidding_home')
    
    return redirect('bid_item_detail', pk=pk)

@login_required
def my_bid_items(request):
    user_items = BidItem.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'user_items': user_items,
        'active_count': user_items.filter(status='active').count(),
        'sold_count': user_items.filter(status='sold').count()
    }
    return render(request, 'bidding/my_bid_items.html', context)

@login_required
def my_bids(request):
    user_bids = Bid.objects.filter(user=request.user).order_by('-created_at')
    bid_items = BidItem.objects.filter(bids__user=request.user).distinct()
    
    winning_bids = []
    for item in bid_items:
        highest_bid = item.bids.first()
        if highest_bid and highest_bid.user == request.user:
            winning_bids.append(item.id)
    
    context = {
        'user_bids': user_bids,
        'bid_items': bid_items,
        'winning_bids': winning_bids
    }
    return render(request, 'bidding/my_bids.html', context)

@login_required
def notifications(request):
    notifications = BidNotification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.GET.get('mark_read'):
        notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    return render(request, 'bidding/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        notification = get_object_or_404(BidNotification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def get_time_remaining(request, pk):
    bid_item = get_object_or_404(BidItem, pk=pk)
    return JsonResponse({
        'time_remaining': bid_item.time_remaining(),
        'has_ended': bid_item.has_ended()
    })

@login_required
def get_current_price(request, pk):
    bid_item = get_object_or_404(BidItem, pk=pk)
    return JsonResponse({
        'current_price': float(bid_item.current_price),
        'bid_count': bid_item.bid_count()
    })

@login_required
def get_unread_notifications_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    
    unread_count = BidNotification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': unread_count})

def serve_template_image(request, image_name):
    template_dir = os.path.join(settings.BASE_DIR, 'bidding', 'templates', 'bidding')
    image_path = os.path.join(template_dir, image_name)
    
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'))
    raise Http404("Image does not exist")


# admin_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Min, Max
from django.core.paginator import Paginator
from django.http import JsonResponse
from bidding.models import BidItem, Bid, BidNotification
from django.contrib.auth.models import User

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_staff
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Dashboard statistics
    total_items = BidItem.objects.all().count()
    active_items = BidItem.objects.filter(status='active').count()
    sold_items = BidItem.objects.filter(status='sold').count()
    expired_items = BidItem.objects.filter(status='expired').count()
    
    total_bids = Bid.objects.all().count()
    total_users = User.objects.all().count()
    
    # Top bidders
    top_bidders = User.objects.annotate(
        bid_count=Count('user_bids')
    ).order_by('-bid_count')[:5]
    
    # Most active items
    active_bid_items = BidItem.objects.filter(status='active').annotate(
        bid_count=Count('bids')
    ).order_by('-bid_count')[:5]
    
    # Recent bids
    recent_bids = Bid.objects.select_related('user', 'bid_item').order_by('-created_at')[:10]
    
    # Ending soon
    ending_soon = BidItem.objects.filter(
        status='active',
        end_date__gt=timezone.now()
    ).order_by('end_date')[:5]
    
    # Revenue from sold items
    revenue = BidItem.objects.filter(status='sold').aggregate(
        total=Sum('current_price')
    )['total'] or 0
    
    # Daily bids for the past 7 days - add this for the activity chart
    today = timezone.now().date()
    daily_bids = []
    for i in range(7, 0, -1):
        day = today - timezone.timedelta(days=i-1)
        count = Bid.objects.filter(created_at__date=day).count()
        daily_bids.append({
            'date': day.strftime('%b %d'),  # Format as 'Apr 10' etc.
            'count': count
        })
    
    context = {
        'total_items': total_items,
        'active_items': active_items,
        'sold_items': sold_items,
        'expired_items': expired_items,
        'total_bids': total_bids,
        'total_users': total_users,
        'top_bidders': top_bidders,
        'active_bid_items': active_bid_items,
        'recent_bids': recent_bids,
        'ending_soon': ending_soon,
        'revenue': revenue,
        'daily_bids': daily_bids,  # Add this to the context
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@user_passes_test(is_admin)
def manage_items(request):
    items = BidItem.objects.all().order_by('-created_at')
    
    # Filter options
    status_filter = request.GET.get('status', '')
    if status_filter:
        items = items.filter(status=status_filter)
    
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(title__icontains=search_query)
    
    # Pagination
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_dashboard/manage_items.html', context)

@user_passes_test(is_admin)
def manage_bids(request):
    bids = Bid.objects.select_related('user', 'bid_item').order_by('-created_at')
    
    # Filter options
    user_filter = request.GET.get('user', '')
    if user_filter:
        bids = bids.filter(user__username__icontains=user_filter)
    
    item_filter = request.GET.get('item', '')
    if item_filter:
        bids = bids.filter(bid_item__title__icontains=item_filter)
    
    # Pagination
    paginator = Paginator(bids, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_filter': user_filter,
        'item_filter': item_filter,
    }
    
    return render(request, 'admin_dashboard/manage_bids.html', context)

@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.annotate(
        bid_count=Count('user_bids'),
        item_count=Count('bid_items')
    ).order_by('-date_joined')
    
    # Filter options
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(username__icontains=search_query)
    
    # Pagination
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'admin_dashboard/manage_users.html', context)

@user_passes_test(is_admin)
def item_detail(request, pk):
    item = get_object_or_404(BidItem, pk=pk)
    bids = item.bids.select_related('user').order_by('-created_at')
    
    context = {
        'item': item,
        'bids': bids,
    }
    
    return render(request, 'admin_dashboard/item_detail.html', context)

@user_passes_test(is_admin)
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_bids = user.user_bids.select_related('bid_item').order_by('-created_at')
    user_items = user.bid_items.order_by('-created_at')
    
    context = {
        'profile_user': user,
        'user_bids': user_bids,
        'user_items': user_items,
    }
    
    return render(request, 'admin_dashboard/user_detail.html', context)


@user_passes_test(is_admin)
def end_auction(request, pk):
    """Show the confirmation page for ending an auction"""
    bid_item = get_object_or_404(BidItem, pk=pk)
    return render(request, 'admin_dashboard/end_confirmation.html', {'item': bid_item})
@user_passes_test(is_admin)
def end_auction_confirm(request, pk):
    """Process the auction end after confirmation"""
    bid_item = get_object_or_404(BidItem, pk=pk)
    
    if request.method == 'POST':
        # Store the highest bidder info before deleting bids if needed
        highest_bidder = bid_item.highest_bidder() if bid_item.bid_count() > 0 else None
        
        # Delete all bids associated with this auction
        Bid.objects.filter(bid_item=bid_item).delete()
        
        # Update the auction status
        if highest_bidder:
            # If there were bids, mark as sold
            bid_item.status = 'sold'
            
            # Notify the highest bidder that they won, even though their bid record is deleted
            BidNotification.objects.create(
                user=highest_bidder,
                bid_item=bid_item,
                notification_type='won',
                message=f"You've won the auction for '{bid_item.title}' with your bid of ${bid_item.current_price}."
            )
        else:
            # If no bids, mark as expired
            bid_item.status = 'expired'
        
        bid_item.save()
        
        # Notify the item owner
        BidNotification.objects.create(
            user=bid_item.user,
            bid_item=bid_item,
            notification_type='ended',
            message=f"Your auction '{bid_item.title}' has been ended by an administrator. All bids have been removed."
        )
        
        messages.success(request, f'Auction "{bid_item.title}" has been ended successfully and all bids have been deleted.')
        return redirect('dashboard')
    
    return redirect('end_auction', pk=pk)


@user_passes_test(is_admin)
def confirm_delete_bid(request, pk):
    # Get the bid object or return 404
    bid = get_object_or_404(Bid, id=pk)
    
    # Render the confirmation page with the bid details
    return render(request, 'admin_dashboard/confirm_delete_bid.html', {
        'bid': bid
    })

def delete_bid(request, pk):
    # Only allow POST requests for deletion
    if request.method == 'POST':
        # Get the bid object or return 404
        bid = get_object_or_404(Bid, id=pk)
        
        try:
            # Store the item ID to redirect back to manage_bids
            bid.delete()
            messages.success(request, "Bid deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting bid: {str(e)}")
        
        # Redirect back to the manage bids page
        return redirect('manage_bids')
    
    # If not POST, redirect to the confirmation page
    return redirect('confirm_delete_bid', bid_id=pk)
@user_passes_test(is_admin)
def analytics(request):
    # Time-based metrics
    today = timezone.now().date()
    
    # Daily bids for the past 7 days
    daily_bids = []
    for i in range(7, 0, -1):
        day = today - timezone.timedelta(days=i-1)
        count = Bid.objects.filter(created_at__date=day).count()
        daily_bids.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Daily new items for the past 7 days
    daily_items = []
    for i in range(7, 0, -1):
        day = today - timezone.timedelta(days=i-1)
        count = BidItem.objects.filter(created_at__date=day).count()
        daily_items.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Category distribution
    category_stats = {}
    for item in BidItem.objects.all():
        category = item.related_item.category if item.related_item and hasattr(item.related_item, 'category') else 'Uncategorized'
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
    
    # Status distribution
    status_stats = BidItem.objects.values('status').annotate(count=Count('id'))
    
    # Bid price distribution
    price_ranges = [
        {'min': 0, 'max': 10, 'count': 0},
        {'min': 10, 'max': 50, 'count': 0},
        {'min': 50, 'max': 100, 'count': 0},
        {'min': 100, 'max': 500, 'count': 0},
        {'min': 500, 'max': 1000, 'count': 0},
        {'min': 1000, 'max': None, 'count': 0},
    ]
    
    for bid in Bid.objects.all():
        for price_range in price_ranges:
            if price_range['min'] <= bid.amount and (price_range['max'] is None or bid.amount <= price_range['max']):
                price_range['count'] += 1
                break
    
    context = {
        'daily_bids': daily_bids,
        'daily_items': daily_items,
        'category_stats': category_stats,
        'status_stats': status_stats,
        'price_ranges': price_ranges,
    }
    
    return render(request, 'admin_dashboard/analytics.html', context)