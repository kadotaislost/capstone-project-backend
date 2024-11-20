import cv2
import requests
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HandwritingAnalysisTable
from .serializers import HandwritingAnalysisSerializer
from mltu.configs import BaseModelConfigs
import google.generativeai as genai
import os
from django.conf import settings
from .predict import ImageToWordModel
from rest_framework.permissions import IsAuthenticated # Ensure correct import based on your project structure
import tempfile



# Load model configurations and initialize the model globally
configs = BaseModelConfigs.load("configs.yaml")
model = ImageToWordModel(model_path="model.onnx", char_list=configs.vocab)


class HandwritingAnalysisView(APIView):
    """
    API view to process an image URL, recognize handwriting, analyze text, and save to the database.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Extract image_url from the request
        image_url = request.data.get('image_url')
        if not image_url:
            return Response({"error": "image_url is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 1: Download the image from the URL
            response = requests.get(image_url)
            if response.status_code != 200:
                return Response({"error": "Failed to download image"}, status=status.HTTP_400_BAD_REQUEST)

            # Decode the image from the response content
            image_data = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

            # Step 2: Predict the recognized text using the model
            recognized_text = model.predict(image)

            # Step 3: Analyze the recognized text using Gemini API
            analyzed_text = self.analyze_text_with_gemini(recognized_text)

            # Step 4: Save the results to the database
            analysis = HandwritingAnalysisTable.objects.create(
                user=request.user,  # Associate the analysis with the authenticated user
                image_url=image_url,
                recognized_text=recognized_text,
                analyzed_text=analyzed_text
            )

            # Step 5: Serialize the saved instance and return the response
            serializer = HandwritingAnalysisSerializer(analysis)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def analyze_text_with_gemini(self, text):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Updated Prompt for the AI model
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
            # Generate response using the Gemini API
            response = model.generate_content(prompt)
            analysis = response.text  # Access the `text` property of the `GenerateContentResponse` object
            return analysis

        except Exception as e:
            # Handle errors gracefully and return a placeholder message
            return f"An error occurred while analyzing the text: {str(e)}"
