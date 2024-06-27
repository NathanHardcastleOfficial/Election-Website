from .models import Constituency,Parties
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