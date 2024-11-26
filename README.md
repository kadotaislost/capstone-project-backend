## Overview

This is the backend for the PrescriptAid application, a revolutionary mobile app designed to leverage Artificial Intelligence (AI) and machine learning to transform handwritten doctors' prescriptions into readable digital text. PrescriptAid aims to reduce confusion and errors in interpreting handwritten prescriptions, enhancing patient safety and trust between doctors and patients.

## What This Backend Contributes

The backend of PrescriptAid plays a crucial role in:

- **User Management**: Securely handling user registration, authentication, and profile management.
- **Prescription Analysis**: Allowing users to upload images of handwritten prescriptions, using AI models to recognize and digitize the text, and providing detailed information about medications, including uses, side effects, and interactions.
- **Medication Reminders**: Sending notifications to remind users about their medication schedules.
- **Data Storage and Retrieval**: Efficiently storing and retrieving user data, prescription details, and medication information.

## Key Features

- **User Registration and Authentication**: Secure user registration and authentication using JWT tokens.
- **Prescription Analysis**: Users can upload images of handwritten prescriptions, which are processed by AI models to recognize and digitize the text. The backend provides detailed information about medications, including uses, side effects, and interactions.
- **Medication Reminders**: Sends notifications to remind users about their medication schedules.
- **User Profile Management**: Allows users to update their profile information, including email, full name, phone number, and profile picture.

## Technologies Used

- **Django**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Django REST Framework**: A powerful and flexible toolkit for building Web APIs.
- **PostgreSQL**: A powerful, open-source object-relational database system.
- **JWT**: JSON Web Tokens for secure user authentication.
- **AI and Machine Learning Models**: Utilizing CNN, and RNN for handwriting recognition.
