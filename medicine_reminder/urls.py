from django.urls import path
from .views import ReminderCreateView, ReminderListView, ReminderView, ReminderUpdateView

urlpatterns = [
    path('reminders/', ReminderListView.as_view(), name='reminder-list'),
    path('reminders/create/', ReminderCreateView.as_view(), name='reminder-create'),
    path('reminders/<int:pk>/', ReminderView.as_view(), name='reminder-detail'),
    path('reminders/<int:pk>/update/', ReminderUpdateView.as_view(), name='reminder-update'),
]