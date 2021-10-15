from django.http.response import HttpResponse
from django.shortcuts import render

from rest_framework import viewsets

from .models import Group
from .serializers import GroupSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset= Group.objects.all()
    serializer_class = GroupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
        return HttpResponse("Yaaaa")