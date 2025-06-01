<div align="center">
  <img src="icon.png" alt="Linkedrite">
</div>

<!-- ![GitHub commit activity](https://img.shields.io/github/commit-activity/:interval/zpratikpathak/Linkedrite) -->
<!-- ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/zpratikpathak/https%3A%2F%2Fgithub.com%2Fzpratikpathak%2FLinkedrite/Deploy%20to%20server) -->



Linkedrite 🤖 is a tool designed to help you craft professional LinkedIn posts. It can correct grammar, generate relatable context, add emojis 😃, format your post, and much more. You can use Linkedrite in two ways: either by installing the extension or by visiting our website, [Linkedrite](https://linkedrite.pratikpathak.com).

# Features 🌟

Linkedrite offers a range of features to help you craft professional LinkedIn posts:

1. **Engaging First Line**: Linkedrite writes an engaging first line that grabs the reader's attention and compels them to read the entire article. With AI-generated suggestions, you can create a captivating opening that piques curiosity and entices readers to explore the rest of your content.
2. **Grammar Correction**: Linkedrite can correct grammatical errors in your posts to ensure they are professional and polished.
3. **Context Generation**: Linkedrite can generate relatable context for your posts based on the initial input.
4. **Emoji Addition**: Linkedrite can add relevant emojis to your posts to make them more engaging.
5. **Post Formatting**: Linkedrite can format your posts to ensure they are easy to read and professional-looking.

# Usage 🚀

Here's how you can use Linkedrite:

1. **Install the Extension**: Install the Linkedrite extension in your browser. Once installed, you can use Linkedrite directly from your LinkedIn post editor.
2. **Use the Website**: Visit [Linkedrite](https://Linkedrite.pratikpathak.com) and enter your initial post. Linkedrite will generate a professional post for you.

For detailed usage instructions, please refer to the Installation section.


# Installation 🛠️

You can install Linkedrite using either Poetry or the requirements.txt file.

## Install via UV 📚

```cmd
poetry sync
```
>Make sure you have already installed UV, if not run this command `pip install uv`

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
