from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Constituency
from .stats import baseVoteshare

def index(request):
    constituency_list = Constituency.objects.order_by("name")
    context = {"constituency_list": constituency_list}
    return render(request, "models/index.html", context)

def constituency(request, constituency_id):
    constituency = get_object_or_404(Constituency, pk=constituency_id)
    projection = baseVoteshare(constituency)
    pr_winner = max(projection, key=projection.get)
    context = {"constituency": constituency, "projection": projection, "pr_winnner": pr_winner}
    return render(request, "models/constituency.html", context)
