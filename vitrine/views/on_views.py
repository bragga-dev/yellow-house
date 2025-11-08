
from django.shortcuts import render



def on_view(request):
    return render(request, 'vitrine/on_view.html')