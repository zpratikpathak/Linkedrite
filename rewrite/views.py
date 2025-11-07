from django.shortcuts import render, redirect
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .models import APICounter
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import throttle_classes
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from subscriptions.models import UsageTracking, Subscription, SubscriptionPlan
from django.utils import timezone
import pytz
from datetime import datetime, timedelta


load_dotenv(".env")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("API_VERSION")
azure_endpoint = os.getenv("AZURE_API_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_MODEL")

client = AzureOpenAI(
    api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint
)


# Create your views here.
def index(request):
    # Show landing page for non-authenticated users
    if not request.user.is_authenticated:
        return render(request, "rewrite/landing.html")
    
    # Show rewrite interface for authenticated users
    context = {"title": "Rewrite"}
    
    # Get user's subscription and usage info
    subscription = getattr(request.user, 'subscription', None)
    if not subscription:
        subscription = Subscription.objects.create(
            user=request.user,
            plan=SubscriptionPlan.FREE
        )
    
    usage = UsageTracking.get_or_create_today(request.user)
    
    context.update({
        'subscription': subscription,
        'current_usage': usage.count,
        'daily_limit': subscription.get_daily_limit(),
        'can_use': usage.can_use(),
    })
    
    return render(
        request=request,
        template_name="rewrite/rewrite_app.html",
        context=context,
    )


# def rewrite(request):

#     if request.method == "POST":
#         data = json.loads(request.body)
#         if len(data["postInput"]) <= 10:
#             return JsonResponse(
#                 {"success": False, "message": "The length of the post is too short."}
#             )
#         print(data)
#         client = AzureOpenAI(
#             api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint
#         )

#         prompt = "Consider yourself writing a linkedIn post now Rewrite the following text and make it more engaging and attractive. Correct the Grammar. It should have professional tone. The post is public, it should be in indirect speech. It should be clear and precise. Only return the rewritten text."
#         if data["emojiNeeded"]:
#             prompt += " Add emojis to make it more engaging."
#         prompt += "\n Now rewrite this text:" + data["postInput"]
#         print("Prompt:", prompt)
#         response = client.completions.create(
#             model=deployment_name,
#             prompt=prompt,
#             # temperature=0.8,
#             max_tokens=1000,
#             # best_of=5,
#         )
#         print(response.choices[0].message.content)
#         return JsonResponse({"success": True, "rewriteAI": response.choices[0].message.content})
#     return JsonResponse({"success": False})


@throttle_classes([UserRateThrottle])
class RewriteAPI(APIView):
    def post(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "message": "Please login to use this service."},
                status=401,
            )
        
        # Check usage limits
        usage = UsageTracking.get_or_create_today(request.user)
        if not usage.can_use():
            subscription = getattr(request.user, 'subscription', None)
            limit = subscription.get_daily_limit() if subscription else 20
            return Response(
                {
                    "success": False, 
                    "message": f"You've reached your daily limit of {limit} rewrites. Upgrade to Premium for unlimited rewrites!",
                    "upgrade_url": "/pricing/"
                },
                status=429,
            )
        
        counter, created = APICounter.objects.get_or_create(pk=1)
        counter.count += 1
        counter.save()
        
        data = request.data
        # print(data)
        if len(data["postInput"]) <= 10:
            return Response(
                {"success": False, "message": "The length of the post is too short."},
                status=400,
            )

        # prompt = (
        #     "You are an expert LinkedIn content writer. Rewrite the following post to be more engaging, "
        #     "professional, and grammatically correct. Instructions:\n"
        #     "- Maintain the original number of paragraphs and overall format\n"
        #     "- Use professional tone and indirect speech\n"
        #     "- Make the content clear, precise, and engaging\n"
        #     "- Rewrite any questions in a more professional manner\n"
        #     "- Provide only the rewritten text without quotation marks or extra spaces\n"
        # )

        # if data["emojiNeeded"]:
        #     prompt += "- Include appropriate emojis to enhance engagement\n"

        # if data["htagNeeded"]:
        #     prompt += "- Add relevant hashtags to increase visibility\n"
        # else:
        #     prompt += "- Do not include hashtags\n"

        # prompt += "\nOriginal post:\n" + data["postInput"]
        # print("Prompt:", prompt)

        # prompt = "Rewrite the following LinkedIn post to make it more engaging, attractive, and professional. Correct any grammar errors, maintain the same number of paragraphs and format, and use indirect speech. The post is public, so it should be clear and precise. Do not enclose the text in quotes or add blank spaces at the start or end of the text."
        # if data["emojiNeeded"]:
        #     prompt += " Include emojis for added engagement."
        # if data["htagNeeded"]:
        #     prompt += " Include relevant hashtags for visibility."
        # else:
        #     prompt += " Do not include hashtags."

        # prompt += "\nHere's the original post: " + data["postInput"]

        # print("Prompt:", prompt)

        messages = [
            {
                "role": "system",
                "content": "You are an expert LinkedIn content writer who creates engaging, professional content with correct grammar.",
            },
            {
                "role": "user",
                "content": f"""
        Rewrite the following LinkedIn post according to these guidelines:
        - Maintain the original number of paragraphs and overall format
        - Use professional tone and indirect speech
        - Make the content clear, precise, and engaging
        - Rewrite any questions in a more professional manner
        {"- Include appropriate emojis to enhance engagement" if data["emojiNeeded"] else ""}
        {"- Add relevant hashtags to increase visibility" if data["htagNeeded"] else "- Do not include hashtags"}

        Original post:
        {data["postInput"]}
        """,
            },
        ]

        response = client.chat.completions.create(
            messages=messages,
            model=deployment_name,
            max_tokens=1000,
            temperature=0.7,  # adding temperature to introduce creativity
            response_format={"type": "text"},
        )
        # print("Answer", response.choices[0].message.content)
        # removing starting and ending blank lines
        response.choices[0].message.content = response.choices[
            0
        ].message.content.strip()
        
        # Increment usage count
        usage.increment()

        return Response(
            {
                "success": True, 
                "rewriteAI": response.choices[0].message.content,
                "usage": {
                    "used": usage.count,
                    "limit": usage.user.subscription.get_daily_limit() if hasattr(usage.user, 'subscription') else 20,
                }
            }
        )

    def get(self, request):
        return Response({"success": False})


@login_required
def dashboard(request):
    """User dashboard showing usage stats and subscription info"""
    user = request.user
    subscription = getattr(user, 'subscription', None)
    
    # Get or create subscription if it doesn't exist
    if not subscription:
        subscription = Subscription.objects.create(
            user=user,
            plan=SubscriptionPlan.FREE
        )
    
    # Get current usage
    usage = UsageTracking.get_or_create_today(user)
    
    # Calculate reset time in user's timezone
    user_tz = pytz.timezone(user.timezone)
    reset_time_local = usage.reset_time.astimezone(user_tz)
    
    # Get usage history for the last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    usage_history = UsageTracking.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    context = {
        'subscription': subscription,
        'current_usage': usage.count,
        'daily_limit': subscription.get_daily_limit(),
        'reset_time': reset_time_local,
        'usage_history': usage_history,
        'can_use': usage.can_use(),
        'current_date': timezone.now().date(),
    }
    
    return render(request, 'rewrite/dashboard_modern.html', context)


def pricing(request):
    """Pricing page showing available plans"""
    user_subscription = None
    if request.user.is_authenticated:
        user_subscription = getattr(request.user, 'subscription', None)
    
    context = {
        'user_subscription': user_subscription,
    }
    
    return render(request, 'rewrite/pricing_modern.html', context)


@login_required
def upgrade_plan(request):
    """Handle plan upgrade requests"""
    if request.method == 'POST':
        # For now, this will be manual through admin
        # In the future, this will integrate with payment gateway
        messages.info(request, 'Please contact support to upgrade your plan.')
        return redirect('rewrite:pricing')
    
    return redirect('rewrite:pricing')


def error_404(request, exception):
    return render(request, "404.html", {})
