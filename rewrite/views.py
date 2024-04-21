from django.shortcuts import render


# Create your views here.
def index(request):

    if request.method == "POST":
        postInput = request.POST.get("postInput", None)
        print(postInput)
    return render(
        request=request,
        template_name="rewrite/index.html",
        context={"title": "Rewrite"},
    )
