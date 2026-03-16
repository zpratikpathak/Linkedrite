import os
import logging
from urllib.parse import urlencode

import httpx
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_USERINFO_URL = 'https://api.linkedin.com/v2/userinfo'
LINKEDIN_POSTS_URL = 'https://api.linkedin.com/rest/posts'
LINKEDIN_IMAGES_URL = 'https://api.linkedin.com/rest/images'

SCOPES = 'openid profile email w_member_social'


def get_client_id():
    return os.getenv('LINKEDIN_CLIENT_ID', '')


def get_client_secret():
    return os.getenv('LINKEDIN_CLIENT_SECRET', '')


def get_redirect_uri():
    return os.getenv('LINKEDIN_REDIRECT_URI', '')


def build_authorization_url(state: str) -> str:
    params = {
        'response_type': 'code',
        'client_id': get_client_id(),
        'redirect_uri': get_redirect_uri(),
        'state': state,
        'scope': SCOPES,
    }
    return f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token."""
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': get_client_id(),
        'client_secret': get_client_secret(),
        'redirect_uri': get_redirect_uri(),
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(LINKEDIN_TOKEN_URL, data=data)
        resp.raise_for_status()
        return resp.json()


def fetch_user_profile(access_token: str) -> dict:
    """Fetch the authenticated user's profile via OpenID Connect userinfo."""
    headers = {'Authorization': f'Bearer {access_token}'}
    with httpx.Client(timeout=30) as client:
        resp = client.get(LINKEDIN_USERINFO_URL, headers=headers)
        resp.raise_for_status()
        return resp.json()


def save_linkedin_account(user, token_data: dict, profile_data: dict):
    """Create or update a LinkedInAccount from OAuth data."""
    from .models import LinkedInAccount

    linkedin_id = profile_data.get('sub', '')
    display_name = profile_data.get('name', '')
    picture = profile_data.get('picture', '')

    expires_in = token_data.get('expires_in', 5184000)  # default 60 days
    token_expires_at = timezone.now() + timedelta(seconds=expires_in)

    account, _ = LinkedInAccount.objects.update_or_create(
        linkedin_id=linkedin_id,
        defaults={
            'user': user,
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', ''),
            'token_expires_at': token_expires_at,
            'display_name': display_name,
            'profile_picture_url': picture,
            'profile_url': f'https://www.linkedin.com/in/{linkedin_id}',
            'is_active': True,
        },
    )
    return account


def create_text_post(access_token: str, linkedin_person_id: str, text: str) -> dict:
    """Create a text-only post on LinkedIn using the Posts API."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202503',
    }
    body = {
        'author': f'urn:li:person:{linkedin_person_id}',
        'commentary': text,
        'visibility': 'PUBLIC',
        'distribution': {
            'feedDistribution': 'MAIN_FEED',
            'targetEntities': [],
            'thirdPartyDistributionChannels': [],
        },
        'lifecycleState': 'PUBLISHED',
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(LINKEDIN_POSTS_URL, headers=headers, json=body)
        resp.raise_for_status()
        post_id = resp.headers.get('x-restli-id', '')
        return {'post_id': post_id, 'status': resp.status_code}


def initialize_image_upload(access_token: str, linkedin_person_id: str) -> dict:
    """Register an image upload with LinkedIn and get the upload URL."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202503',
    }
    body = {
        'initializeUploadRequest': {
            'owner': f'urn:li:person:{linkedin_person_id}',
        }
    }
    url = f'{LINKEDIN_IMAGES_URL}?action=initializeUpload'
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()['value']


def upload_image_binary(upload_url: str, access_token: str, image_bytes: bytes) -> None:
    """Upload raw image bytes to the LinkedIn upload URL."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
    }
    with httpx.Client(timeout=60) as client:
        resp = client.put(upload_url, headers=headers, content=image_bytes)
        resp.raise_for_status()


def create_image_post(
    access_token: str,
    linkedin_person_id: str,
    text: str,
    image_bytes: bytes,
    alt_text: str = '',
) -> dict:
    """Upload an image and create a post with it on LinkedIn."""
    upload_data = initialize_image_upload(access_token, linkedin_person_id)
    upload_url = upload_data['uploadUrl']
    image_urn = upload_data['image']

    upload_image_binary(upload_url, access_token, image_bytes)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202503',
    }
    body = {
        'author': f'urn:li:person:{linkedin_person_id}',
        'commentary': text,
        'visibility': 'PUBLIC',
        'distribution': {
            'feedDistribution': 'MAIN_FEED',
            'targetEntities': [],
            'thirdPartyDistributionChannels': [],
        },
        'lifecycleState': 'PUBLISHED',
        'content': {
            'media': {
                'title': alt_text or 'Image',
                'id': image_urn,
                'altText': alt_text,
            }
        },
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(LINKEDIN_POSTS_URL, headers=headers, json=body)
        resp.raise_for_status()
        post_id = resp.headers.get('x-restli-id', '')
        return {'post_id': post_id, 'status': resp.status_code}
