from .models import Constituency,Parties,TotalSeats,Result,Projection
from django.forms.models import model_to_dict
from math import exp,log

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

def projectionVoteshare(projection):
    values = {}
    if projection.con:
        values[Parties.CON] = projection.con
    if projection.lab:
        values[Parties.LAB] = projection.lab
    if projection.ld:
        values[Parties.LD] = projection.ld
    if projection.ref:
        values[Parties.REF] = projection.ref
    if projection.grn:
        values[Parties.GRN] = projection.grn
    if projection.snp:
        values[Parties.SNP] = projection.snp
    if projection.pc:
        values[Parties.PC] = projection.pc
    if projection.min:
        values[Parties.OTH] = projection.min
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
        if constituency.result:
            party = constituency.result.winner
            if party not in projected_counts:
                projected_counts[party] = 0
                declared_counts[party] = 0
            projected_counts[party] += 1
            declared_counts[party] += 1
        else:
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

def resultVotes(result):
    party_capitalisations = {'con': 'Con', 'lab': 'Lab', 'ld': 'LD', 'ref': 'Ref', 'grn': 'Grn', 'snp': 'SNP', 'pc': 'PC', 'wpb': 'WPB', 'alba': 'Alba', 'ukip': 'UKIP', 'sdp': 'SDP', 'ind': 'Ind', 'oth': 'Oth'}
    votes = {party_capitalisations[k[:-6]]: v for k,v in model_to_dict(result).items() if ((v != None) and (k not in ("winner","id","total_votes")))}
    return votes

def doBasicProjection():
    party_capitalisations = {'con': 'Con', 'lab': 'Lab', 'ld': 'LD', 'ref': 'Ref', 'grn': 'Grn', 'snp': 'SNP', 'pc': 'PC', 'min': 'Oth'}
    results = Constituency.objects.exclude(result__isnull=True)
    deltas = {"Con": 0, "Lab": 0, "LD": 0, "Ref":0, "Grn":0, "SNP":0, "PC":0}
    counts = {"Con": 1, "Lab": 1, "LD": 1, "Ref":1, "Grn":1, "SNP":1, "PC":1}
    for result in results:
        if (result.result.con_votes != None) and (result.base_con != None):
            deltas["Con"] += log(result.result.con_votes/result.result.total_votes)+log(7)-float(result.base_con)
            counts["Con"] += 1
        if  (result.result.lab_votes != None) and (result.base_lab != None):
            deltas["Lab"] += log(result.result.lab_votes/result.result.total_votes)+log(7)-float(result.base_lab)
            counts["Lab"] += 1
        if  (result.result.ld_votes != None) and (result.base_ld != None):
            deltas["LD"] += log(result.result.ld_votes/result.result.total_votes)+log(7)-float(result.base_ld)
            counts["LD"] += 1
        if  (result.result.ref_votes != None) and (result.base_ref != None):
            deltas["Ref"] += log(result.result.ref_votes/result.result.total_votes)+log(7)-float(result.base_ref)
            counts["Ref"] += 1
        if  (result.result.grn_votes != None) and (result.base_grn != None):
            deltas["Grn"] += log(result.result.grn_votes/result.result.total_votes)+log(7)-float(result.base_grn)
            counts["Grn"] += 1
        if  (result.result.snp_votes != None) and (result.base_snp != None):
            deltas["SNP"] += log(result.result.snp_votes/result.result.total_votes)+log(7)-float(result.base_snp)
            counts["SNP"] += 1
        if  (result.result.pc_votes != None) and (result.base_pc != None):
            deltas["PC"] += log(result.result.pc_votes/result.result.total_votes)+log(7)-float(result.base_pc)
            counts["PC"] += 1
    for party, count in counts.items():
        if count < 10:
            counts[party] = counts[party]/2 + 5
    deltas = {k: v/counts[k] for k,v in deltas.items()}
    #print(deltas)
    constituencies = Constituency.objects.all()
    for constituency in constituencies:
        strengths = {}
        if constituency.base_con != None:
            strengths["con"] = float(constituency.base_con)+deltas["Con"]
        if constituency.base_lab != None:
            strengths["lab"] = float(constituency.base_lab)+deltas["Lab"]
        if constituency.base_ld != None:
            strengths["ld"] = float(constituency.base_ld)+deltas["LD"]
        if constituency.base_ref != None:
            strengths["ref"] = float(constituency.base_ref)+deltas["Ref"]
        if constituency.base_grn != None:
            strengths["grn"] = float(constituency.base_grn)+deltas["Grn"]
        if constituency.base_snp != None:
            strengths["snp"] = float(constituency.base_snp)+deltas["SNP"]
        if constituency.base_pc != None:
            strengths["pc"] = float(constituency.base_pc)+deltas["PC"]
        if constituency.base_min != None:
            strengths["min"] = float(constituency.base_min)
        basic_projection = voteshare(strengths)
        basic_projection['detailed'] = False
        basic_projection['winner'] = party_capitalisations[max(basic_projection, key=basic_projection.get)]
        basic_projection = Projection(**basic_projection)
        basic_projection.save()
        constituency.basic_projection = basic_projection
        constituency.save()
    updateTotals()