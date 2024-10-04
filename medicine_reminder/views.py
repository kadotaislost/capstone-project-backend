from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Reminder
from .serializers import ReminderSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class ReminderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReminderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Reminder created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReminderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reminders = Reminder.objects.filter(user=request.user)
        serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReminderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Reminder, pk=pk, user=user)

    def get(self, request, pk):
        reminder = self.get_object(pk, request.user)
        serializer = ReminderSerializer(reminder)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        reminder = self.get_object(pk, request.user)
        reminder.delete()
        return Response({"message": "Reminder deleted successfully"},status=status.HTTP_204_NO_CONTENT)

class ReminderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Reminder, pk=pk, user=user)

    def put(self, request, pk):
        reminder = self.get_object(pk, request.user)
        serializer = ReminderSerializer(reminder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Successfully Updated reminder"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

