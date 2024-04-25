from django.shortcuts import render
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json

load_dotenv(".env")
api_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("API_VERSION")
azure_endpoint = os.getenv("AZURE_API_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_MODEL")


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
#         print(response.choices[0].text)
#         return JsonResponse({"success": True, "rewriteAI": response.choices[0].text})
#     return JsonResponse({"success": False})


class RewriteAPI(APIView):
    def post(self, request):
        data = request.data
        # print(data)
        if len(data["postInput"]) <= 10:
            return Response(
                {"success": False, "message": "The length of the post is too short."},
                status=400,
            )

        client = AzureOpenAI(
            api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint
        )

        prompt = "Consider yourself writing a linkedIn post now Rewrite the following text and make it more engaging and attractive. Correct the Grammar. It should have professional tone. The post is public, it should be in indirect speech. It should be clear and precise. Only return the rewritten text. Do not enclose the text in quotes."
        if data["emojiNeeded"]:
            prompt += " Add emojis to make it more engaging."
        if data["htagNeeded"]:
            prompt += " Add hashtags to make it more engaging."
        else:
            prompt += " Do not add hashtags."
        prompt += "\n Now rewrite this text:" + data["postInput"]

        response = client.completions.create(
            model=deployment_name,
            prompt=prompt,
            max_tokens=1000,
        )

        return Response({"success": True, "rewriteAI": response.choices[0].text})

    def get(self, request):
        return Response({"success": False})
