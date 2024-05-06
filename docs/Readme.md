<div align="center">
  <img src="icon.png" alt="LinkedInAi">
</div>

![GitHub commit activity](https://img.shields.io/github/commit-activity/:interval/zpratikpathak/LinkedinAI)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/zpratikpathak/https%3A%2F%2Fgithub.com%2Fzpratikpathak%2FLinkedinAI/Deploy%20to%20server)



LinkedInAi 🤖 is a tool designed to help you craft professional LinkedIn posts. It can correct grammar, generate relatable context, add emojis 😃, format your post, and much more. You can use LinkedInAi in two ways: either by installing the extension or by visiting our website, [LinkedInAi](https://linkedinai.pratikpathak.com).

# Features 🌟

LinkedInAi offers a range of features to help you craft professional LinkedIn posts:

1. **Grammar Correction**: LinkedInAi can correct grammatical errors in your posts to ensure they are professional and polished.
2. **Context Generation**: LinkedInAi can generate relatable context for your posts based on the initial input.
3. **Emoji Addition**: LinkedInAi can add relevant emojis to your posts to make them more engaging.
4. **Post Formatting**: LinkedInAi can format your posts to ensure they are easy to read and professional-looking.

# Usage 🚀

Here's how you can use LinkedInAi:

1. **Install the Extension**: Install the LinkedInAi extension in your browser. Once installed, you can use LinkedInAi directly from your LinkedIn post editor.
2. **Use the Website**: Visit [LinkedInAi](https://linkedinai.pratikpathak.com) and enter your initial post. LinkedInAi will generate a professional post for you.

For detailed usage instructions, please refer to the Installation section.


# Installation 🛠️

You can install LinkedInAi using either Poetry or the requirements.txt file.

## Install via Poetry 📚

```cmd
poetry run
```
>Make sure you have already installed Poetry, if not run this command `pip install poetry`

<div align="center">

**OR 🔄**

</div>

## Install via Requirements.txt 📄
```cmd
pip install -r requirements.txt
```

## Setup .ENV file 🗂️
Create a `.env` file in the root directory and add the following credentials:
```
AZURE_OPENAI_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxx"
AZURE_API_ENDPOINT = "https://xxxxxxxx.openai.azure.com/"
API_VERSION = "2023-12-01-preview"
DEPLOYMENT_MODEL = "XXXXXXXXXXXXXXXXXXXX"
```
**Note**: Not sure how to get these credentials? Click here to find out.

# How to run 🏃‍♂️
```cmd
python manage.py runserver
```