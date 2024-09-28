from django.urls import path
from . import views

urlpatterns = [
    path('reminders/create/', views.ReminderCreateView.as_view(), name='reminder-create'),
    path('reminders/', views.ReminderListView.as_view(), name='reminder-list'),
    path('reminders/<int:pk>/update/', views.ReminderUpdateView.as_view(), name='reminder-update'),
    path('reminders/<int:pk>/delete/', views.ReminderView.as_view(), name='reminder-delete'),
    path('reminders/<int:pk>/', views.ReminderView.as_view(), name='get-reminder'),
]
