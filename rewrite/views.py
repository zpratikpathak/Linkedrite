from django.shortcuts import render
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

    return render(
        request=request,
        template_name="rewrite/index.html",
        context={"title": "Rewrite"},
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

        return Response(
            {"success": True, "rewriteAI": response.choices[0].message.content}
        )

    def get(self, request):
        return Response({"success": False})


def error_404(request, exception):
    return render(request, "404.html", {})
