from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room, User
from .serializers import RoomSerializer
from django.http import JsonResponse, FileResponse
import json

"""
未來目標(長期)
1. class-based views
"""

@api_view(["GET"])
def get_routes(request):
    routes = [
        "GET /api",
        "GET /api/rooms",
        "GET /api/rooms/:id"
    ]
    return Response(routes)


@api_view(["GET"])
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_one_room(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)
