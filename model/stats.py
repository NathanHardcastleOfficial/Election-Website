from .models import Constituency,Parties,TotalSeats
from math import exp

#takes in a Constituency and returns the base projected voteshare% in a dictionary.
def baseVoteshare(constituency):
    values = {}
    total = 0
    if constituency.base_con != None:
        value = exp(constituency.base_con)
        values[Parties.CON] = value
        total += value
    if constituency.base_lab != None:
        value = exp(constituency.base_lab)
        values[Parties.LAB] = value
        total += value
    if constituency.base_ld != None:
        value = exp(constituency.base_ld)
        values[Parties.LD] = value
        total += value
    if constituency.base_ref != None:
        value = exp(constituency.base_ref)
        values[Parties.REF] = value
        total += value
    if constituency.base_grn != None:
        value = exp(constituency.base_grn)
        values[Parties.GRN] = value
        total += value
    if constituency.base_snp != None:
        value = exp(constituency.base_snp)
        values[Parties.SNP] = value
        total += value
    if constituency.base_pc != None:
        value = exp(constituency.base_pc)
        values[Parties.PC] = value
        total += value
    if constituency.base_min != None:
        value = exp(constituency.base_min)
        values[Parties.OTH] = value
        total += value
    for key in values:
        values[key] = values[key]*100/total
    return values

def voteshare(dict):
    values = {}
    total = 0
    for party, strength in dict.items():
        value = exp(float(strength))
        values[party] = value
        total += value
    for key in values:
        values[key] = values[key]*100/total
    return values

def updateTotals():
    constuency_list = Constituency.objects.all()
    seat_totals = TotalSeats.objects.all()
    for party in seat_totals:
        party.declared = 0
        party.projected = 0
        party.save()
    declared_counts = {}
    projected_counts = {}
    for constituency in constuency_list:
        if constituency.detailed_projection:
            party = constituency.detailed_projection.winner
        elif constituency.basic_projection:
            party = constituency.basic_projection.winner
        else:
            party = constituency.winner2019
        if party not in projected_counts:
            projected_counts[party] = 0
            declared_counts[party] = 0
        projected_counts[party] += 1
    for party in declared_counts:
        party_totals, _ = TotalSeats.objects.get_or_create(party=party)
        party_totals.declared = declared_counts[party]
        party_totals.projected = projected_counts[party]
        party_totals.save()