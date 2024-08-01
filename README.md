# AI Blog Generator

This Django-based application automatically converts YouTube video content into blog posts. It uses speech-to-text technology from Assembly AI to generate video transcript and generative AI to create blog post from the transcription.

## Features

- User authentication system
- YouTube video URL input
- Blog article generation from the content of a youtube video
- MongoDB integration for storing blog posts
- User-friendly interface for viewing generated blog posts

## Technologies Used

- Django
- MongoDB
- Generative AI (Model: gemini-pro)
- AssemblyAI API
- HTML/CSS/JavaScript

## Setup

1. **Clone the repository:** 
    `git clone https://github.com/kalyan-sama/AI-Blog-Generator.git`

2. **Configuration:**
   - Create a `.env` file in the root of the project.
   - Add following vairables:
    ```
    GENAI_API_KEY = <your GenAI API key>
    AAI_API_KEY = <your Assembly AI API key>
    DB_HOST = <your MongoDB connection url>
    DB_USERNAME = <your MongoDB username>
    DB_PASSWORD = <your MongoDB password>
    ```

3. **Environment activation:**
   - Create a virtual environment: `python -m venv venv`
   - Activate the virtual environment: `venv\Scripts\activate`

4. **Install Dependencies:**
   - Install required packages: `pip install -r requirements.txt`

5. **Run migrations:**
    `python manage.py migrate`

6. **Start the development server:**
    `python manage.py runserver`

## Usage

1. Sign up or log in to your account.
2. Enter a YouTube video URL.
3. Wait for the conversion process to complete.
4. View the generated blog post.
5. Access the previously created in `Saved Articles`