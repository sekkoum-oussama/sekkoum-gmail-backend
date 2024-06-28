import os
import json
from django.http import JsonResponse
from django.conf import settings


def serve_assetlinks(request):
    # Define the path to the assetlinks.json file
    file_path = os.path.join(settings.BASE_DIR, '.well-known', 'assetlinks.json')
    
    # Open and read the content of the JSON file
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    return JsonResponse(data, safe=False)