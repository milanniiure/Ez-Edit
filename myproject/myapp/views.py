from django.shortcuts import render
from django.http import HttpResponse
import cv2
import numpy as np

def home(request):
    return render(request, 'home.html')

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_image = request.FILES['image']
        
        # Read the uploaded image using OpenCV
        image_data = uploaded_image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Perform image processing tasks here (e.g., convert to grayscale)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Save the processed image to a file (optional)
        processed_image_path = "path/to/save/processed/image.jpg"
        cv2.imwrite(processed_image_path, gray_image)

        # Return an HttpResponse indicating success
        return HttpResponse('Image uploaded and processed successfully!')

    return render(request, 'upload_image.html')
