from django.urls import path
from . import views

urlpatterns = [
    # User-facing URLs
    path('', views.bidding_home, name='bidding_home'),
    path('items/', views.BidItemListView.as_view(), name='bid_item_list'),
    path('items/<int:pk>/', views.BidItemDetailView.as_view(), name='bid_item_detail'),
    path('add/', views.add_bid_item, name='add_bid_item'),
    path('items/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('my-items/', views.my_bid_items, name='my_bid_items'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('notifications/', views.notifications, name='bid_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # AJAX endpoints
    path('items/<int:pk>/time-remaining/', views.get_time_remaining, name='get_time_remaining'),
    path('items/<int:pk>/current-price/', views.get_current_price, name='get_current_price'),
    path('unread-notifications-count/', views.get_unread_notifications_count, name='get_unread_notifications_count'),
    
    # Static file serving
    path('template-image/<str:image_name>/', views.serve_template_image, name='bidding_image'),
    # admin_dashboard/urls.py


    path('bidding_dashboard/', views.admin_dashboard, name='dashboard'),
    path('items/', views.manage_items, name='manage_items'),
    path('bids/', views.manage_bids, name='manage_bids'),
    path('users/', views.manage_users, name='manage_users'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    # path('items/<int:pk>/end/', views.end_auction, name='end_auction'),
    path('bids/<int:pk>/delete/', views.delete_bid, name='delete_bid'),
    path('analytics/', views.analytics, name='analytics'),
   path('bids/<int:pk>/confirm-delete/', views.confirm_delete_bid, name='confirm_delete_bid'),
path('bids/<int:pk>/delete/', views.delete_bid, name='delete_bid'),
   path('items/<int:pk>/end/', views.end_auction, name='end_auction'),
path('items/<int:pk>/end/confirm/', views.end_auction_confirm, name='end_auction_confirm'),  # Fixed the closing bracket

    
]

# In your project's main urls.py, you would add:
# path('admin-dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
