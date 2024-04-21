from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
import os
import assemblyai as aai
import google.generativeai as genai 
from .models import BlogPost
from dotenv import load_dotenv

load_dotenv()

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            yt_link = data['link']
            # print("yt_link: ", yt_link)
            #return JsonResponse({'content': yt_link})
        except(KeyError, json.JSONDecodeError):
            return JsonResponse({"Error": "Invalid request method"}, status = 400)
            
        # get YT title
        print("Getting YT title")
        title = get_yt_title(yt_link)
        print("title: ", title)
        print("user:", request.user, type(request.user))
        print()

        # get transcript
        print("Getting transcript")
        transcription = get_transcriptions(yt_link)
        if not transcription:
            return JsonResponse({"Error": "Failed to get transcript"}, status = 500)
        print("Transcript generated successfully")
        print("--------------------------------")

        # use Google GenAI to generate blog
        print("Generating blog post using Google GenAI")
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({"Error": "Failed to generate blog article"}, status = 500)
        
        print("Blog post generated successfully")
        print("-------------------------------- ")
        print("saving blog post to database...")

        # save blog to database
        try:
            print("request.user.is_authenticated == ", request.user.is_authenticated)
            if request.user.is_authenticated:
                # user_instance = User.objects.get(username=str(request.user))
                # user_instance = User.objects.get(username=request.user.username)
                user_instance = request.user
                print("user_instance: ", user_instance, type(user_instance))
                new_blog_article = BlogPost.objects.create(
                    user=user_instance,
                    youtube_title=title,
                    youtube_link=yt_link,
                    generated_content=blog_content,
                )
                new_blog_article.save()
                
        except Exception as e:
            print("Could not save blog post with error: " + str(e))

        print("blog saved to database successfully")
        print("--------------------------------")

        # return blog as response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({"Error": "Invalid request method"}, status = 405)

def get_yt_title(link):
    try:
        yt = YouTube(link)
        title = yt.title
        return title
    except Exception as e:
        return "Cant Retrieve YouTube title: " + str(e)

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file


def get_transcriptions(link):
    audio_file = download_audio(link)
    aai.settings.api_key = os.getenv("AAI_API_KEY")
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    
    return transcript.text

def generate_blog_from_transcription(transcription):
    prompt = f"Write a blog article from a transcript that I will provide you. Please make it comprehensive and clear which should look like a proper blog article. Here is the transcript: \n\n{transcription}\n\n"

    genai.configure(api_key=os.getenv("GENAI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    generated_content = model.generate_content(prompt)
    # print(generated_content.text)
    return (generated_content.text)

def blogs_list(request):
    blog_articles = BlogPost.objects.filter(user = request.user)
    return render(request, 'all-blogs.html', {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        print(blog_article_detail)
        return render(request, 'blog_details.html', {'blog_article_detail': blog_article_detail})
    else:
        return ('/')
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message} )
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword and password!="":
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = "Error creating user account"
                return render(request, 'signup.html', {'error_message': error_message} )

        else:
            error_message = "Password does not match"
            return render(request, 'signup.html', {'error_message': error_message} )

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')

