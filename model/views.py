from django.shortcuts import get_object_or_404, render
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django import forms
from .models import Constituency, TotalSeats, Result
from .stats import baseVoteshare,resultVotes,projectionVoteshare,doBasicProjection

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

class ResultForm(forms.Form):
    constituency = forms.ModelChoiceField(queryset=Constituency.objects.all(), widget=forms.Select(attrs={'class': 'constituency-dropdown'}))
    con_votes = forms.IntegerField(label='Conservative Votes', min_value=0, required=False)
    lab_votes = forms.IntegerField(label='Labour Votes', min_value=0, required=False)
    ld_votes = forms.IntegerField(label='Lib Dem Votes', min_value=0, required=False)
    snp_votes = forms.IntegerField(label='SNP Votes', min_value=0, required=False)
    grn_votes = forms.IntegerField(label='Green Votes', min_value=0, required=False)
    ref_votes = forms.IntegerField(label='Reform UK Votes', min_value=0, required=False)
    pc_votes = forms.IntegerField(label='Plaid Cymru Votes', min_value=0, required=False)
    wpb_votes = forms.IntegerField(label='WPB Votes', min_value=0, required=False)
    sdp_votes = forms.IntegerField(label='SDP Votes', min_value=0, required=False)
    ukip_votes = forms.IntegerField(label='UKIP Votes', min_value=0, required=False)
    alba_votes = forms.IntegerField(label='Alba Votes', min_value=0, required=False)
    ind_votes = forms.IntegerField(label='Independent Votes', min_value=0, required=False)
    oth_votes = forms.IntegerField(label='Other Party Votes', min_value=0, required=False)

def addResults(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ResultForm(request.POST)
        if form.is_valid():
            party_capitalisations = {'con': 'Con', 'lab': 'Lab', 'ld': 'LD', 'ref': 'Ref', 'grn': 'Grn', 'snp': 'SNP', 'pc': 'PC', 'wpb': 'WPB', 'alba': 'Alba', 'ukip': 'UKIP', 'sdp': 'SDP', 'ind': 'Ind', 'oth': 'Oth'}
            result = {k: v for k,v in form.cleaned_data.items() if k != "constituency"}
            constituency = form.cleaned_data["constituency"]
            filtered_result = {k: v for k, v in result.items() if v != None}
            result["total_votes"] = sum(value for value in filtered_result.values())
            result["winner"] = party_capitalisations[max(filtered_result, key=filtered_result.get)[:-6]]
            new_result = Result(**result)
            new_result.save()
            constituency.result = new_result
            constituency.save()
            doBasicProjection()
            call_command("clean_projections")
            return HttpResponseRedirect(reverse("model:main"))
    else:
        form = ResultForm()
    return render(request, "models/resultentry.html", {'form': form})