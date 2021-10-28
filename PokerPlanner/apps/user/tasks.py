from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from PokerPlanner.celery import app


@app.task
def send_email_task(first_name, pk, token, email):
    """
    Celery task for sending email
    """
    message = render_to_string('verification_email.html', {
        'username': first_name,
        'domain': settings.BASE_URL_BE,
        'uid': pk,
        'token': token
    })
    subject = "Verify Email"
    try:
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, 
        recipient_list=[email], fail_silently=False)
    except:
        print("Error Occured")


@app.task
def send_invite_task(email):
    """
    Celery task for sending invite email
    """
    message = render_to_string('signup_email.html', {
        'domain': settings.BASE_URL_BE,
    })
    subject = "Invite Email"
    try:
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, 
        recipient_list=[email], fail_silently=False)
    except:
        print("Error Occured")
        