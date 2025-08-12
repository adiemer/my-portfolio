from rest_framework import viewsets
from .models import Project, Experience
from .serializers import ProjectSerializer, ExperienceSerializer
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from portfolio_backend.settings import MONGO_DB
from unittest.mock import patch
from django.test import TestCase, Client

about_collection = MONGO_DB["about"]

@require_http_methods(["GET"])
def get_about(request):
    about_data = about_collection.find_one()
    if about_data:
        about_data["_id"] = str(about_data["_id"])
        return JsonResponse({"message":about_data})
    return JsonResponse({"error": "No About data found"}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def update_about(request):
    try:
        data = json.loads(request.body)
        required_fields = ["name", "title", "bio", "skills"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        # Clear old content
        about_collection.delete_many({})
        result = about_collection.insert_one(data)
        return JsonResponse({"inserted_id": str(result.inserted_id)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@patch("api.views.about_collection")
def test_get_about_not_found(self, mock_collection):
    mock_collection.find_one.return_value = None
    response = self.client.get('/api/about/')
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response.json(), {"error": "No About data found"})
    
@patch("api.views.about_collection")
def test_update_about_success(self, mock_collection):
    mock_collection.insert_one.return_value.inserted_id = "abc123"

    valid_data = {
        "name": "Andrew D",
        "title": "Developer",
        "bio": "Loves Python and Docker",
        "skills": ["Python", "React"]
    }

    response = self.client.post(
        "/api/about/",
        data=json.dumps(valid_data),
        content_type="application/json"
    )

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), {"inserted_id": "abc123"})
    
@patch("api.views.about_collection")
def test_update_about_missing_fields(self, mock_collection):
    invalid_data = {
        "name": "Andrew D",
        "bio": "Missing title and skills"
    }

    response = self.client.post(
        "/api/about/",
        data=json.dumps(invalid_data),
        content_type="application/json"
    )

    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json(), {"error": "Missing required fields"})


        

def test_mongo(request):
    about_col = MONGO_DB['about']
    about_col.insert_one({"test": "Hello from Docker Mongo!"})
    data = about_col.find_one({"test": "Hello from Docker Mongo!"})
    data["_id"] = str(data["_id"])
    return JsonResponse({"mongo_data": data})

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer

class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer