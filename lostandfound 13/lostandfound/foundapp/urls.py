from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main pages
    path('', views.main_page, name='main'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # FAQ and questions
    path('faq/', views.faq_view, name='faq'),
    path('questions/', views.questions_view, name='questions'),
    path('submit-question/', views.submit_question, name='submit_question'),
     path('faq/delete/<int:question_id>/', views.faq_delete_question, name='faq_delete_question'),

    # Profile management
    path('profile/', views.profile_page, name='profile_page'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
     
    # Item management
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_new'),
    path('items/add/', views.add_item, name='add_item'),
    path('items/<int:pk>/update/', views.update_item, name='update_item'),
    path('items/<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('items/image/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path('items/my-items/', views.my_items, name='my_items'),

    # Admin dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin-dashboard/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-dashboard/promote-user/<int:user_id>/', views.admin_promote_user, name='admin_promote_user'),
    path('admin-dashboard/handle-request/<int:request_id>/<str:action>/',
         views.admin_handle_request, name='admin_handle_request'),
    path('admin-dashboard/add-task/', views.admin_add_task, name='admin_add_task'),
    path('admin-dashboard/complete-task/<int:task_id>/', views.admin_complete_task, name='admin_complete_task'),
    path('admin-dashboard/delete-task/<int:task_id>/', views.admin_delete_task, name='admin_delete_task'),
    path('admin-dashboard/users/', views.admin_view_all_users, name='admin_view_all_users'),
    path('admin-dashboard/items/', views.admin_view_all_items, name='admin_view_all_items'),
    path('admin-dashboard/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-dashboard/users/toggle-status/<int:user_id>/',
         views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin-dashboard/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-dashboard/questions/', views.admin_view_user_questions, name='admin_view_user_questions'),
    path('admin-dashboard/questions/delete/<int:question_id>/',
         views.admin_delete_question, name='admin_delete_question'),
     path('admin-dashboard/questions/reply/<int:question_id>/', views.admin_reply_question, name='admin_reply_question'),
      path('user-faq/', views.user_faq_view, name='user_faq'),
         path('items/<int:item_id>/submit-found/', views.submit_found_claim, name='submit_found_claim'),
    path('items/<int:item_id>/submit-ownership/', views.submit_ownership_claim, name='submit_ownership_claim'),
    path('claims/<int:claim_id>/status/', views.claim_status, name='claim_status'),
    path('my-claims/', views.manage_claims, name='manage_claims'),
    path('claims/<int:claim_id>/', views.claim_detail, name='claim_detail'),

]
