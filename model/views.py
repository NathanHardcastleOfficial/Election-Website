from django.shortcuts import get_object_or_404, render
from django.forms.models import model_to_dict
from django.http import HttpResponse
from .models import Constituency, TotalSeats
from .stats import baseVoteshare,resultVotes,projectionVoteshare

def index(request):
    constituency_list = Constituency.objects.order_by("name")
    party_totals = TotalSeats.objects.order_by("-projected")
    overall_result = {"winner": party_totals[0].party, "majority": 2*party_totals[0].projected-650}
    context = {"constituency_list": constituency_list, "party_totals": party_totals, "overall_result": overall_result}
    return render(request, "models/index.html", context)

def constituency(request, constituency_id):
    constituency = get_object_or_404(Constituency, pk=constituency_id)
    if constituency.result:
        projection = resultVotes(constituency.result)
        pr_winner = constituency.result.winner
    else:
        if constituency.detailed_projection:
            projection = projectionVoteshare(constituency.detailed_projection)
            pr_winner = constituency.detailed_projection.winner
        elif constituency.basic_projection:
            projection = projectionVoteshare(constituency.basic_projection)
            pr_winner = constituency.basic_projection.winner
        else:
            projection = baseVoteshare(constituency)
            pr_winner = max(projection, key=projection.get)
    context = {"constituency": constituency, "projection": projection, "pr_winnner": pr_winner}
    return render(request, "models/constituency.html", context)
