from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import JsonResponse

# Home view
def home(request):
    return render(request, 'home.html')

# Index view for login/signup page
def index(request):
    return render(request, 'index.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('index')  # Redirect to the index page for login

    return render(request, 'index.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if username or email is already registered
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
            return redirect('index')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('index')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('index')

        # Create user if all validations pass
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "✅ Registration successful..!! You can now log in.")
        return redirect('index')  # Redirect to index after signup

    return render(request, 'index.html', {'show_signup': True})

# Forgot Password View with OTP and password reset handling
class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'email.html', {'otp_sent': False, 'otp_verified': False})

    def post(self, request):
        # Step 1: Handle OTP request
        if 'email' in request.POST:
            email = request.POST.get('email')
            otp = get_random_string(length=4, allowed_chars='0123456789')
            
            # Store OTP and email in session for verification
            request.session['otp'] = otp
            request.session['email'] = email
            
            # Send the OTP via email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP has been sent to your email.')
            return render(request, 'email.html', {'otp_sent': True, 'otp_verified': False})

        # Step 2: Handle OTP verification
        if 'otp-0' in request.POST:
            user_otp = ''.join([request.POST.get(f'otp-{i}') for i in range(4)])  # Collect OTP from inputs
            session_otp = request.session.get('otp')
            email = request.session.get('email')

            if user_otp == session_otp:
                # OTP is correct, show password reset fields
                return render(request, 'email.html', {'otp_sent': True, 'otp_verified': True})

            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'email.html', {'otp_sent': True, 'otp_verified': False})

        # Step 3: Handle password reset after OTP verification
        if 'new-password' in request.POST:
            new_password = request.POST.get('new-password')
            confirm_password = request.POST.get('confirm-password')

            # Validate that the passwords match
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'email.html', {'otp_sent': True, 'otp_verified': True})

            # Update the password
            user = User.objects.get(email=request.session['email'])
            user.set_password(new_password)
            user.save()

            # Clear session data and redirect to login
            del request.session['otp']
            del request.session['email']
            messages.success(request, '✅ Password has been reset successfully! Please log in.')
            return redirect('login')

        return render(request, 'email.html', {'otp_sent': False, 'otp_verified': False})


# views.py
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render

def check_username(request):
    if request.method == "GET":
        username = request.GET.get('username', None)
        if username:
            user_exists = User.objects.filter(username=username).exists()
            return JsonResponse({'exists': user_exists})
        return JsonResponse({'exists': False})

def check_email(request):
    if request.method == "GET":
        email = request.GET.get('email', None)
        if email:
            email_exists = User.objects.filter(email=email).exists()
            return JsonResponse({'exists': email_exists})
        return JsonResponse({'exists':False})
    
    
def profile_view(request):
    return render(request, 'profile.html')

def voice_view(request):
    return render(request, 'voice.html')

def subscription_view(request):
    return render(request, 'subscription.html')

def help_view(request):
    return render(request, 'help.html')

def settings_view(request):
    return render(request, 'settings.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import UserProfile

@login_required
def profile_view(request):
    user = request.user

    # Try to fetch an existing UserProfile; create a new one if not found
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Handle form submission
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('profile')  # Redirect to the same page after saving
    else:
        # Render the form with current data
        form = UserProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'user': user})






from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from google.cloud import vision
from google.cloud import texttospeech
import os
import base64

# Google Vision API client
vision_client = vision.ImageAnnotatorClient()

# Google Cloud Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

def index(request):
    """Render the image upload and capture page."""
    return render(request, 'index.html')

def capture_image(request):
    """Capture or upload an image, process it for text detection, and convert the text to speech."""
    if request.method == 'POST':
        image_data = None
        
        # Check if an image is uploaded
        if 'upload_image' in request.FILES:
            uploaded_image = request.FILES['upload_image']
            image_data = uploaded_image.read()
        elif 'captured_image' in request.POST:
            # For webcam-captured image (base64 string)
            base64_image = request.POST['captured_image'].split(',')[1]
            image_data = base64.b64decode(base64_image)
        else:
            return JsonResponse({'message': 'No image provided'}, status=400)

        # Convert the image to Google Vision format
        image = vision.Image(content=image_data)

        # Perform text detection using Google Vision
        response = vision_client.document_text_detection(image=image)
        annotations = response.full_text_annotation

        if annotations and annotations.text:
            recognized_text = annotations.text

            # Determine the language of the text (example: Hindi, Kannada)
            language_code = "hi-IN" if "ह" in recognized_text else "kn-IN" if "ಕ" in recognized_text else "en-US"

            # Convert the recognized text to speech using Google Text-to-Speech
            synthesis_input = texttospeech.SynthesisInput(text=recognized_text)

            # Set voice parameters (language and gender)
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            # Set audio configuration (MP3 format)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Perform the text-to-speech request
            response = tts_client.synthesize_speech(
                request={'input': synthesis_input, 'voice': voice, 'audio_config': audio_config}
            )

            # Save the audio response as an MP3 file
            audio_content = response.audio_content
            audio_file_name = 'recognized_text.mp3'
            audio_file_path = os.path.join('media', audio_file_name)

            # Save the audio file to the media directory
            with open(audio_file_path, 'wb') as out:
                out.write(audio_content)

            # Return the recognized text and audio file path
            return JsonResponse({
                'recognized_text': recognized_text,
                'audio_file': audio_file_name
            })
        else:
            return JsonResponse({'message': 'No text detected in the image'}, status=200)

    return HttpResponse(status=400)
