from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
import logging

from .forms import (
    SignUpForm, CustomLoginForm, ItemForm, ItemImageForm,
    UserUpdateForm, ProfileUpdateForm, DeleteAccountForm
)
from .models import Item, ItemImage, UserQuestion, UserProfile

def main_page(request):
    lost_items = Item.objects.filter(item_type='lost').order_by('-date_created')[:6]
    found_items = Item.objects.filter(item_type='found').order_by('-date_created')[:6]
    context = {
        'lost_items': lost_items,
        'found_items': found_items,
    }
    return render(request, 'main.html', context)

# ========== Authentication ==========

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('main')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


import logging

import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            role = request.POST.get('role')

            logger.debug(f"--- Login Attempt ---")
            logger.debug(f"Username: '{username}'")
            logger.debug(f"Selected Role (form): '{role}'")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    profile = UserProfile.objects.get(user=user)
                    user_role = profile.role
                    logger.debug(f"User's Actual Role (DB): '{user_role}'")

                    # Add these lines for detailed logging
                    logger.debug(f"Raw form role: {repr(role)}")
                    logger.debug(f"Raw database role: {repr(user_role)}")

                    if role == user_role:
                        logger.debug("Role check: MATCH")
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.username}!")

                        if user_role == 'admin':
                            logger.debug("Redirecting to: main")
                            return redirect('admin_dashboard')
                        else:
                            logger.debug("Redirecting to: profile_page")
                            return redirect('main')
                    else:
                        logger.debug("Role check: MISMATCH")
                        messages.error(request, "Invalid role for this user.")
                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
                    return render(request, 'login.html', {'form': form})
            else:
                logger.debug("Authentication: FAILED")
                messages.error(request, "Invalid username or password.")
        else:
            logger.debug("Form: INVALID")
            messages.error(request, "Invalid form data.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main')

# ========== FAQ ==========

def faq_view(request):
    questions = UserQuestion.objects.all()
    return render(request, 'faqs.html', {'questions': questions})

def submit_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        if question:
            UserQuestion.objects.create(question=question)
            messages.success(request, 'Your question has been submitted.')
        else:
            messages.error(request, 'Please enter a question.')
    return redirect('faq')

# ========== Profile ==========


@login_required
def profile_page(request):
    # Get the user's items
    user_items = Item.objects.filter(user=request.user).order_by('-date_created')
    
    # Count statistics
    lost_items = user_items.filter(item_type='lost').count()
    found_items = user_items.filter(item_type='found').count()
    resolved_items = user_items.filter(is_resolved=True).count() 
    
    # Get the user's claims
    # user_claims = Claim.objects.filter(user=request.user)
    
    # Get resolved claims (claims that have been approved)
    # resolved_claims = Claim.objects.filter(user=request.user, status='approved')
    
    context = {
        'user_items': user_items[:5],  # Keep the original limit of 5 items
        'lost_items': lost_items,
        'found_items': found_items,
        'resolved_items': resolved_items,
        # 'user_claims': user_claims,
        # 'resolved_claims': resolved_claims,  # Add the resolved claims to the context
    }
    return render(request, 'profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_page')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'update_profile.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user:
                logout(request)
                user.delete()
                messages.success(request, 'Your account has been permanently deleted.')
                return redirect('main')
            else:
                messages.error(request, 'Incorrect password.')
    else:
        form = DeleteAccountForm()
    return render(request, 'delete_account.html', {'form': form})


# ------myitem-------
class ItemListView(ListView):
    model = Item
    template_name = 'items/item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by type if specified
        item_type = self.request.GET.get('type')
        if item_type in ['lost', 'found']:
            queryset = queryset.filter(item_type=item_type)
            
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(
                description__icontains=search_query
            ) | queryset.filter(
                location__icontains=search_query
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_type'] = self.request.GET.get('type', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ItemDetailView(DetailView):
    model = Item
    template_name = 'items/item_detail.html'
    context_object_name = 'item'

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('image')
            for image in images:
                ItemImage.objects.create(item=item, image=image)
            
            messages.success(request, 'Your item has been added successfully!')
            return redirect('item_new', pk=item.pk)
    else:
        form = ItemForm()
        image_form = ItemImageForm()
    
    return render(request, 'items/item_form.html', {
        'form': form,
        'image_form': image_form,
        'title': 'Add Item'
    })

@login_required
def update_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    # Check if user is the owner
    if item.user != request.user and request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to edit this item.")
        return redirect('item_new', pk=item.pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        
        if form.is_valid():
            form.save()
            
            # Handle image uploads
            images = request.FILES.getlist('image')
            for image in images:
                ItemImage.objects.create(item=item, image=image)
            
            messages.success(request, 'Your item has been updated successfully!')
            return redirect('item_new', pk=item.pk)
    else:
        form = ItemForm(instance=item)
        image_form = ItemImageForm()
    
    return render(request, 'items/item_form.html', {
        'form': form,
        'image_form': image_form,
        'item': item,
        'title': 'Update Item'
    })

@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    # Check if user is the owner
    if item.user != request.user and request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to delete this item.")
        return redirect('item_new', pk=item.pk)

    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Your item has been deleted successfully!')
        return redirect('item_list')
    
    return render(request, 'items/item_confirm_delete.html', {'item': item})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ItemImage, id=image_id)
    item = image.item
    
    # Check if user is the owner
    if item.user != request.user:
        return JsonResponse({'success': False, 'message': "You don't have permission to delete this image."})
    
    image.delete()
    return JsonResponse({'success': True})

@login_required
def my_items(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'items/my_items.html', {'items': items})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from .models import UserProfile, Item, ItemImage,AdminRequest, Bid
import logging

# Set up logger
logger = logging.getLogger(__name__)


@login_required
def admin_dashboard(request):
    # Check if user is admin
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('main')
    
    # Get all users, lost items, and found items
    users = User.objects.all().order_by('-date_joined')
    lost_items = Item.objects.filter(item_type='lost').order_by('-date_created')
    found_items = Item.objects.filter(item_type='found').order_by('-date_created')
    
    # Get pending admin requests
    admin_requests = AdminRequest.objects.filter(status='pending')
    
    # Get bid information
    bids = Bid.objects.all().order_by('-created_at')
    
    context = {
        'users': users,
        'lost_items': lost_items,
        'found_items': found_items,
        'total_users': users.count(),
        'total_lost': lost_items.count(),
        'total_found': found_items.count(),
        'resolved_items': Item.objects.filter(is_resolved=True).count(),
        'admin_requests': admin_requests,
        'bids': bids,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_user_detail(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('main')
    
    try:
        user = User.objects.get(id=user_id)
        user_items = Item.objects.filter(user=user)
        user_bids = Bid.objects.filter(user=user)
        
        context = {
            'viewed_user': user,
            'user_items': user_items,
            'user_bids': user_bids,
        }
        return render(request, 'admin_user_detail.html', context)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('admin_dashboard')

@login_required
def admin_delete_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                messages.error(request, "You cannot delete your own account from here.")
            else:
                username = user.username
                user.delete()
                messages.success(request, f"User {username} has been deleted successfully.")
            return redirect('admin_dashboard')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    
    return redirect('admin_dashboard')

@login_required
def admin_promote_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.profile.role = 'admin'
            user.profile.save()
            messages.success(request, f"{user.username} has been promoted to admin.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    
    return redirect('admin_dashboard')

@login_required
def admin_handle_request(request, request_id, action):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    try:
        admin_request = AdminRequest.objects.get(id=request_id)
        
        if action == 'approve':
            admin_request.status = 'approved'
            admin_request.user.profile.role = 'admin'
            admin_request.user.profile.save()
            messages.success(request, f"{admin_request.user.username}'s admin request has been approved.")
        elif action == 'reject':
            admin_request.status = 'rejected'
            messages.success(request, f"{admin_request.user.username}'s admin request has been rejected.")
        
        admin_request.save()
    except AdminRequest.DoesNotExist:
        messages.error(request, "Request not found.")
    
    return redirect('admin_dashboard')

# @login_required
# def request_admin_access(request):
#     if request.method == 'POST':
#         reason = request.POST.get('reason')
#         if not reason:
#             messages.error(request, "Please provide a reason for your request.")
#             return redirect('profile_page')
        
#         # Check if user already has a pending request
#         if AdminRequest.objects.filter(user=request.user, status='pending').exists():
#             messages.error(request, "You already have a pending admin request.")
#             return redirect('profile_page')
        
#         # Create new request
#         AdminRequest.objects.create(
#             user=request.user,
#             reason=reason
#         )
        
#         messages.success(request, "Your request for admin access has been submitted and is pending approval.")
#         return redirect('profile_page')
    
#     return render(request, 'request_admin.html')


    # ... existing imports ...
from django.utils import timezone
from django.db.models import Count, Sum
from .models import UserProfile, Item, ItemImage, AdminRequest, Bid, AdminTask
import datetime
import json

# ... existing code ...

@login_required
def admin_dashboard(request):
    # Check if user is admin
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('main')
    
    # Get all users, lost items, and found items
    users = User.objects.all().order_by('-date_joined')
    lost_items = Item.objects.filter(item_type='lost').order_by('-date_created')
    found_items = Item.objects.filter(item_type='found').order_by('-date_created')
    
    # Get pending admin requests
    admin_requests = AdminRequest.objects.filter(status='pending')
    
    # Get bid information
    bids = Bid.objects.all().order_by('-created_at')
    
    # Get admin tasks (to-do list)
    admin_tasks = AdminTask.objects.filter(completed=False).order_by('due_date')
    
    # Get dates for to-do list
    today = timezone.now()
    tomorrow = today + datetime.timedelta(days=1)
    next_week = today + datetime.timedelta(days=7)
    
    # Generate data for the chart - last 7 days of user registrations
    days = 7
    date_range = [today - datetime.timedelta(days=i) for i in range(days)]
    date_range.reverse()
    
    # Format dates for display
    week_days = [day.strftime('%b %d') for day in date_range]
    
    # Count users registered each day
    this_week_data = []
    last_week_data = []
    
    for day in date_range:
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # This week's data
        count = User.objects.filter(date_joined__range=(day_start, day_end)).count()
        this_week_data.append(count)
        
        # Last week's data (7 days before)
        last_week_day_start = day_start - datetime.timedelta(days=7)
        last_week_day_end = day_end - datetime.timedelta(days=7)
        last_week_count = User.objects.filter(date_joined__range=(last_week_day_start, last_week_day_end)).count()
        last_week_data.append(last_week_count)
    
    # Get recent user activity
    recent_users = []
    recent_user_objects = users[:4]  # Get 4 most recent users
    
    for user in recent_user_objects:
        # Get user's most recent activity
        user_items = Item.objects.filter(user=user).order_by('-date_created').first()
        user_bids = Bid.objects.filter(user=user).order_by('-created_at').first()
        
        action = "New registration"
        timestamp = user.date_joined
        
        if user_items and (not user_bids or user_items.date_created > user_bids.created_at):
            action = f"Added item: {user_items.name}"
            timestamp = user_items.date_created
        elif user_bids:
            action = f"Placed bid on item"
            timestamp = user_bids.created_at
        
        recent_users.append({
            'user': user,
            'action': action,
            'timestamp': timestamp
        })
    
    context = {
        'users': users,
        'lost_items': lost_items,
        'found_items': found_items,
        'total_users': users.count(),
        'total_lost': lost_items.count(),
        'total_found': found_items.count(),
        'resolved_items': Item.objects.filter(is_resolved=True).count(),
        'admin_requests': admin_requests,
        'bids': bids,
        'admin_tasks': admin_tasks,
        'today': today,
        'tomorrow': tomorrow,
        'next_week': next_week,
        'this_week_data': json.dumps(this_week_data),
        'last_week_data': json.dumps(last_week_data),
        'week_days': week_days,
        'recent_users': recent_users,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_add_task(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    if request.method == 'POST':
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        due_date_str = request.POST.get('due_date')
        
        if not task_title:
            messages.error(request, "Task title is required.")
            return redirect('admin_dashboard')
        
        try:
            # Parse the due date if provided
            if due_date_str:
                due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                due_date = timezone.make_aware(datetime.datetime.combine(due_date, datetime.time(18, 0)))
            else:
                due_date = timezone.now() + datetime.timedelta(days=1)
            
            # Create the task
            AdminTask.objects.create(
                title=task_title,
                description=task_description,
                due_date=due_date,
                created_by=request.user
            )
            
            messages.success(request, "Task added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding task: {str(e)}")
        
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')

@login_required
def admin_complete_task(request, task_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    try:
        task = AdminTask.objects.get(id=task_id)
        task.completed = True
        task.completed_at = timezone.now()
        task.completed_by = request.user
        task.save()
        
        messages.success(request, "Task marked as completed.")
    except AdminTask.DoesNotExist:
        messages.error(request, "Task not found.")
    
    return redirect('admin_dashboard')

@login_required
def admin_delete_task(request, task_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    try:
        task = AdminTask.objects.get(id=task_id)
        task.delete()
        
        messages.success(request, "Task deleted successfully.")
    except AdminTask.DoesNotExist:
        messages.error(request, "Task not found.")
    
    return redirect('admin_dashboard')

@login_required
def admin_view_all_users(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('main')
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Filter users based on search query
    if search_query:
        users = User.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).order_by('-date_joined')
    else:
        users = User.objects.all().order_by('-date_joined')
    
    # Add pagination if needed
    context = {
        'users': users,
        'total_users': User.objects.count(),
        'search_query': search_query,
    }
    
    return render(request, 'admin_users.html', context)

@login_required
def admin_view_all_items(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('main')
    
    items = Item.objects.all().order_by('-date_created')
    
    # Filter by type if specified
    item_type = request.GET.get('type')
    if item_type in ['lost', 'found']:
        items = items.filter(item_type=item_type)
    
    context = {
        'items': items,
        'total_items': items.count(),
        'item_type': item_type or 'all',
    }
    
    return render(request, 'items/item_list.html', context)

# ... rest of the existing code ...


@login_required
def admin_edit_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    try:
        user_to_edit = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('admin_view_all_users')
    
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        
        # Update user information
        user_to_edit.username = username
        user_to_edit.email = email
        user_to_edit.first_name = first_name
        user_to_edit.last_name = last_name
        
        # Update profile if it exists
        if hasattr(user_to_edit, 'profile'):
            user_to_edit.profile.role = role
            user_to_edit.profile.save()
        
        user_to_edit.save()
        messages.success(request, f"User {username} has been updated successfully.")
        return redirect('admin_view_all_users')
    
    context = {
        'user_to_edit': user_to_edit
    }
    return render(request, 'admin_edit_user.html', context)

@login_required
def admin_toggle_user_status(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    try:
        user_to_toggle = User.objects.get(id=user_id)
        
        # Don't allow deactivating yourself
        if user_to_toggle == request.user:
            messages.error(request, "You cannot deactivate your own account.")
            return redirect('admin_view_all_users')
        
        # Toggle the active status
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()
        
        status = "activated" if user_to_toggle.is_active else "deactivated"
        messages.success(request, f"User {user_to_toggle.username} has been {status} successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    return redirect('admin_view_all_users')

@login_required
def admin_delete_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('main')
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Don't allow deleting yourself
        if user_to_delete == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect('admin_view_all_users')
        
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"User {username} has been deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    return redirect('admin_view_all_users')


@login_required
def admin_view_user_questions(request):
    questions = UserQuestion.objects.all()
    return render(request, 'question.html', {'questions': questions})


@login_required  # Protect this view (if only admins should delete)
def delete_question(request, question_id):
    """
    Deletes a user question from the database.

    Args:
        request: The Django request object.
        question_id: The ID of the question to delete.
    """
    try:
        question = get_object_or_404(UserQuestion, id=question_id)
        question.delete()
        messages.success(request, "Question deleted successfully.")
    except UserQuestion.DoesNotExist:
        messages.error(request, "Question not found.")
    return redirect('faq')  # Or whatever URL you want to redirect to


@login_required  # Protect this view (if only admins should delete)
# @user_passes_test(lambda u: u.profile.role == 'admin')  # If only admins can delete
def admin_delete_question(request, question_id):
    """
    Deletes a user question from the admin dashboard.

    Args:
        request: The Django request object.
        question_id: The ID of the question to delete.
    """
    try:
        question = get_object_or_404(UserQuestion, id=question_id)
        question.delete()
        messages.success(request, "Question deleted successfully.")
    except UserQuestion.DoesNotExist:
        messages.error(request, "Question not found.")
    return redirect('admin_view_user_questions')  # Redirect to the admin questions view


def questions_view(request):
    questions = UserQuestion.objects.all()
    return render(request, 'question.html', {'questions': questions})

@login_required
def admin_reply_question(request, question_id):
    """Handles the submission of an admin reply to a user question."""

    question = get_object_or_404(UserQuestion, id=question_id)

    if request.method == 'POST':
        reply_text = request.POST.get('reply')  # Get the reply from the form
        if reply_text:
            question.reply = reply_text
            question.save()
            messages.success(request, "Reply submitted successfully.")
        else:
            messages.error(request, "Please enter a reply.")

    return redirect('admin_view_user_questions')  # Redirect back 

def user_faq_view(request):
    """Displays the FAQ to users, including admin replies."""
    questions = UserQuestion.objects.all().order_by('-submitted_at')  # Order by submission date (newest first)
    return render(request, 'user_faqs.html', {'questions': questions})

@login_required  # Protect this view (if only admins can delete)
def faq_delete_question(request, question_id):
    """Deletes a question from the FAQ."""
    question = get_object_or_404(UserQuestion, id=question_id)
    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect('faq')  # Redirect back to the FAQ page




# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Item, ItemClaim

@require_POST
def submit_found_claim(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # Create claim record
    claim = ItemClaim(
        item=item,
        claim_type='found',
        claimer_name=request.POST.get('found_name'),
        claimer_email=request.POST.get('found_email'),
        claimer_phone=request.POST.get('found_phone'),
        found_location=request.POST.get('found_location'),
        found_date=request.POST.get('found_date'),
        found_description=request.POST.get('found_description'),
    )
    
    # Attach user if logged in
    if request.user.is_authenticated:
        claim.user = request.user
    
    # Handle image upload
    if 'found_image' in request.FILES:
        claim.image = request.FILES['found_image']
    
    claim.save()
    
    # Send notification to item owner (implementation depends on your notification system)
    
    return JsonResponse({
        'success': True,
        'message': 'Your claim has been submitted successfully.',
        'redirect_url': reverse('claim_status', args=[claim.id])
    })

@require_POST
def submit_ownership_claim(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # Create claim record
    claim = ItemClaim(
        item=item,
        claim_type='ownership',
        claimer_name=request.POST.get('claim_name'),
        claimer_email=request.POST.get('claim_email'),
        claimer_phone=request.POST.get('claim_phone'),
        ownership_proof=request.POST.get('claim_proof'),
    )
    
    # Attach user if logged in
    if request.user.is_authenticated:
        claim.user = request.user
    
    # Handle image upload
    if 'claim_image' in request.FILES:
        claim.image = request.FILES['claim_image']
    
    claim.save()
    
    # Send notification to item owner (implementation depends on your notification system)
    
    return JsonResponse({
        'success': True,
        'message': 'Your ownership claim has been submitted successfully.',
        'redirect_url': reverse('claim_status', args=[claim.id])
    })

def claim_status(request, claim_id):
    claim = get_object_or_404(ItemClaim, id=claim_id)
    
    # Only allow access to the claim owner or item owner
    if request.user.is_authenticated:
        if request.user != claim.user and request.user != claim.item.user:
            return redirect('item_new', claim.item.id)
    else:
        # For anonymous users, implement some verification logic
        # e.g., store claim ID in session or use a unique token
        pass
    
    return render(request, 'items/claim_status.html', {
        'claim': claim
    })

@login_required
def manage_claims(request):
    # Get all claims for items owned by the current user
    claims = ItemClaim.objects.filter(item__user=request.user).order_by('-created_at')
    
    return render(request, 'items/manage_claims.html', {
        'claims': claims
    })

@login_required
def claim_detail(request, claim_id):
    claim = get_object_or_404(ItemClaim, id=claim_id)
    
    # Ensure the user is the owner of the claimed item
    if request.user != claim.item.user:
        return redirect('manage_claims')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes')
        
        if action == 'approve':
            claim.approve(notes)
            # Send notification to claimer
            return redirect('manage_claims')
        elif action == 'reject':
            claim.reject(notes)
            # Send notification to claimer
            return redirect('manage_claims')
    
    return render(request, 'items/claim_detail.html', {
        'claim': claim
    })