import cv2
import requests
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HandwritingAnalysisTable
from .serializers import HandwritingAnalysisSerializer , HandwritingAnalysisInputSerializer
from mltu.configs import BaseModelConfigs
import google.generativeai as genai
import os
from django.conf import settings
from .predict import ImageToWordModel
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import get_object_or_404
from django.http import Http404
import tempfile


# Load model configurations and initialize the model globally
configs = BaseModelConfigs.load("configs.yaml")
model = ImageToWordModel(model_path="model.onnx", char_list=configs.vocab)


class HandwritingAnalysisView(APIView):
    """
    API view to process an image URL and  recognize handwriting
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Validate the input data
        serializer = HandwritingAnalysisInputSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_url = serializer.validated_data.get('image_url')

        try:
            # Step 1: Download the image from the URL
            response = requests.get(image_url, timeout=10)  # Adding a timeout for better control
            if response.status_code != 200:
                return Response(
                    {"error": "Failed to download the image", "details": f"HTTP {response.status_code}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Decode the image from the response content
            image_data = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            if image is None:
                return Response(
                    {"error": "Failed to decode the image", "details": "The provided URL does not contain a valid image"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Step 2: Predict the recognized text using the model
            try:
                recognized_text = model.predict(image)
            except Exception as e:
                return Response(
                    {"error": "Handwriting recognition failed", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Step 3: Analyze the recognized text using Gemini API
            analyzed_text = self.analyze_text_with_gemini(recognized_text)

            # Return the results without saving to the database
            return Response(
                {   
                    "image_url": image_url,
                    "recognized_text": recognized_text,
                    "analyzed_text": analyzed_text
                },
                status=status.HTTP_200_OK
            )

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Failed to fetch the image", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def analyze_text_with_gemini(self, text):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        prompt = f"""
        You will analyze the text provided below and determine its nature. Follow these steps:

        1. Check if the text mentions any medicine name(s).  
        - If medicine names are mentioned, extract and correct any spelling or grammatical errors in the medicine names, ensuring accuracy.  
        - Provide structured information about the medicine(s) as outlined below.

        2. If no medicine name is mentioned but the text appears to be general advice or a prescription from a doctor, analyze the text and describe its purpose or rationale in simple, layman-friendly terms.

        For medicine-related information, adhere to this structure for each medicine:

        ---
        Medicine Name:  
        [Provide the corrected and confirmed name of the medicine.]

        Description:  
        [Give a straightforward overview of the medicine, including its purpose and how it works, in simple terms.]

        Uses:  
        [List the main medical conditions the medicine is commonly used for.]

        Side Effects:  
        [Summarize the most common side effects. Briefly mention any serious side effects if applicable.]

        Drug Interactions:  
        [State if the medicine interacts with any common drugs or substances.]

        Dosage Information:  
        [Summarize typical dosage information without recommending any specific doses. Include a reminder that dosage should be determined by a doctor.]

        Precautions:  
        [Provide any important precautions, such as when to avoid the medicine or things to watch out for while using it.]

        ---

        For general advice or non-medicine-related text, use this structure:

        ---
        Advice:  
        [Restate the advice in simpler terms, if needed.]

        Purpose or Rationale:  
        [Explain why this advice is important, what it seeks to achieve, and any potential benefits or consequences of following it.]

        ---

        If the text cannot be analyzed into either category, respond with: "Too little information provided to determine the nature of the text."

        **Additional Guidelines:**  
        - Use simple and clear language suitable for a layperson. Avoid technical or overly scientific terms.  
        - Do not add commentary or assumptions beyond the requested information.  
        - If any section cannot be filled due to lack of data, state "Information not available."  
        - End with this disclaimer: "This information is for educational purposes only and should not replace professional medical advice. Always consult a healthcare provider for advice tailored to your health."

        ---
        
        Recognized Text: {text}

        Please analyze the text and provide a response adhering to the appropriate structure and guidelines.
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred while analyzing the text: {str(e)}"

class HandwritingAnalysisStoreView(APIView):
    """
    API view to store recognized and analyzed data into the database.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Validate the input data
        serializer = HandwritingAnalysisSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Save the data to the database
            serializer.save(user=request.user)
            return Response({"message": "prescription saved successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": "Failed to save prescription", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


   
class UserPrescriptionsView(APIView):
    """
    API view to list all prescriptions of the authenticated user with optional search functionality.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all prescriptions for the authenticated user
        prescriptions = HandwritingAnalysisTable.objects.filter(user=request.user)

        # Check if a search query parameter is provided
        search_query = request.query_params.get('search', None)
        if search_query:
            prescriptions = prescriptions.filter(prescription_name__icontains=search_query)

        if not prescriptions.exists():
            return Response(
                {"message": "No prescriptions found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the data
        serializer = HandwritingAnalysisSerializer(prescriptions, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


        
class PrescriptionDetailView(APIView):
    """
    API view to retrieve and delete a specific prescription by ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, prescription_id):
        try:
            prescription = get_object_or_404(
                HandwritingAnalysisTable,
                id=prescription_id,
                user=request.user
            )
            serializer = HandwritingAnalysisSerializer(prescription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {"error": "Prescription not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, prescription_id):
        try:
            # Get and verify prescription belongs to user
            prescription = get_object_or_404(
                HandwritingAnalysisTable,
                id=prescription_id,
                user=request.user
            )
            
            # Delete the prescription
            prescription.delete()
            
            return Response(
                {"message": "Prescription deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Http404:
            # Handle the case where get_object_or_404 raises a 404
            return Response(
                {"error": "Prescription not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
