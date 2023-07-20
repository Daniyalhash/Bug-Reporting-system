from django.urls import path
from . import views
from .views import *

ReporterID = "abc123"

urlpatterns = [
    path('', home, name='home'),
    path('addBug', addBug, name='addBug'),
    path('record/', record, name='record'),
    path('bugType/', views.bug_types_view, name='bugTypes'),
    # path('url_path/', views.view_function, name='view_function'),
    path('delete_record/<str:ReporterID>/', delete_record, name='delete_record'),
    path('saveform/', saveform, name='saveform'),
    path('update_record/<str:ReporterID>/',update_record,name='update_record'),
    path('get-counts/', views.get_counts, name='get_counts'),
    path('email/', views.email, name='email'),
    path('fetch-bug-types/', views.fetch_bug_types, name='fetch_bug_types'),
    path('fetch-site-names/', views.fetch_site_names, name='fetch_site_names'),
    path('fetch-owner-email/', views.fetch_owner_email, name='fetch_owner_email'),
    path('send-email/', views.send_email, name='send_email'),
    path('update-status/', views.update_status, name='update_status'),
]
