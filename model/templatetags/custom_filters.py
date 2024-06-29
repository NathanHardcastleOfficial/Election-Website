from django import template
from model.models import Parties

register = template.Library()

@register.filter
def long_party_name(value):
    try:
        return Parties(value).label
    except KeyError:
        return value
    
@register.filter
def medium_party_name(value):
    if value == "Con":
        return "Conservative"
    if value == "Lab":
        return "Labour"
    if value == "LD":
        return "Lib Dem"
    if value == "Ref":
        return "Reform UK"
    if value == "Grn":
        return "Green"
    if value == "PC":
        return "Plaid Cymru"
    if value == "Ind":
        return "Independent"
    if value == "Oth":
        return "Other"
    return value

@register.filter
def party_colour(value):
    if value == "Con":
        return "#0087dc"
    if value == "Lab":
        return "#e4003b"
    if value == "LD":
        return "#faa61a"
    if value == "SNP":
        return "#fdf38e"
    if value == "Ref":
        return "#12b6cf"
    if value == "Grn":
        return "#02a95b"
    if value == "PC":
        return "#004A43"
    if value == "WPB":
        return "#780021"
    if value == "Alba":
        return "#005eb8"
    if value == "UKIP":
        return "#6d3177"
    if value == "SDP":
        return "#D25469"
    return "#AAAAAA"

@register.filter
def negate(value):
    return -value