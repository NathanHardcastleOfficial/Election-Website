import pandas as pd
from .models import Constituency,Parties,TotalSeats,Result,Projection
from django.forms.models import model_to_dict
from math import exp,log
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from django.conf import settings

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
            if (constituency.detailed_projection != None) and settings.USE_DETAIL:
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

def _resultToDict(result):
    dict = {k:float(v) for k,v in model_to_dict(result).items() if ((v != None) and (k in ("age_under_25","age_25_34","age_35_49","age_50_64","age_over_65","immigrant","white","religion_christian","religion_islam","religion_hindu","religion_other")))}
    votes = model_to_dict(result.result)
    for party in ["con","lab","ld","snp","grn","ref","pc"]:
        base = getattr(result,"base_"+party)
        if (votes[party+"_votes"] != None) and (base != None) :
            dict[party+"_delta"] = log(votes[party+"_votes"]/votes["total_votes"])+log(7)-float(base)
    dict["name"] = result.name
    return dict

def doDetailedProjection():
    try:
        party_capitalisations = {'con': 'Con', 'lab': 'Lab', 'ld': 'LD', 'ref': 'Ref', 'grn': 'Grn', 'snp': 'SNP', 'pc': 'PC', 'min': 'Oth'}
        imputer = SimpleImputer(strategy='mean')
        columns_to_drop = ['name','con_delta', 'lab_delta', 'ld_delta', 'ref_delta', 'grn_delta', 'snp_delta', 'pc_delta']
        results = Constituency.objects.exclude(result__isnull=True)
        data = [_resultToDict(result) for result in results]
        df = pd.DataFrame(data)
        condf = df.dropna(subset=['con_delta'])
        if len(condf.columns) > 20:
            con = True
            conX = imputer.fit_transform(condf.drop(columns=[col for col in columns_to_drop if col in condf.columns]))
            conY = condf['con_delta']
            conModel = LinearRegression()
            conModel.fit(conX,conY)
        labdf = df.dropna(subset=['lab_delta'])
        if len(labdf.columns) > 20:
            lab = True
            labX = imputer.fit_transform(labdf.drop(columns=[col for col in columns_to_drop if col in labdf.columns]))
            labY = condf['lab_delta']
            labModel = LinearRegression()
            labModel.fit(labX,labY)
        lddf = df.dropna(subset=['ld_delta'])
        if len(lddf.columns) > 20:
            ld = True
            ldX = imputer.fit_transform(lddf.drop(columns=[col for col in columns_to_drop if col in lddf.columns]))
            ldY = condf['ld_delta']
            ldModel = LinearRegression()
            ldModel.fit(ldX,ldY)
        refdf = df.dropna(subset=['ref_delta'])
        if len(refdf.columns) > 20:
            ref = True
            refX = imputer.fit_transform(refdf.drop(columns=[col for col in columns_to_drop if col in refdf.columns]))
            refY = condf['ref_delta']
            refModel = LinearRegression()
            refModel.fit(refX,refY)
        grndf = df.dropna(subset=['grn_delta'])
        if len(grndf.columns) > 20:
            grn = True
            grnX = imputer.fit_transform(grndf.drop(columns=[col for col in columns_to_drop if col in grndf.columns]))
            grnY = condf['grn_delta']
            grnModel = LinearRegression()
            grnModel.fit(grnX,grnY)
        snpdf = df.dropna(subset=['snp_delta'])
        if len(snpdf.columns) > 20:
            snp = True
            snpX = imputer.fit_transform(snpdf.drop(columns=[col for col in columns_to_drop if col in snpdf.columns]))
            snpY = condf['snp_delta']
            snpModel = LinearRegression()
            snpModel.fit(snpX,snpY)
        pcdf = df.dropna(subset=['pc_delta'])
        if len(pcdf.columns) > 20:
            pc = True
            pcX = imputer.fit_transform(pcdf.drop(columns=[col for col in columns_to_drop if col in pcdf.columns]))
            pcY = condf['pc_delta']
            pcModel = LinearRegression()
            pcModel.fit(pcX,pcY)
        constituencies = Constituency.objects.all()
        for constituency in constituencies:
            strengths = {}
            if constituency.base_con != None:
                if con:
                    strengths["con"] = float(constituency.base_con)+conModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif condf.columns > 0:
                    strengths["con"] = float(constituency.base_con)+condf.loc[:,"con_delta"].mean()
                else:
                    strengths["con"] = float(constituency.base_con)
            if constituency.base_lab != None:
                if lab:
                    strengths["lab"] = float(constituency.base_lab)+labModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif labdf.columns > 0:
                    strengths["lab"] = float(constituency.base_lab)+labdf.loc[:,"lab_delta"].mean()
                else:
                    strengths["lab"] = float(constituency.base_lab)
            if constituency.base_ld != None:
                if ld:
                    strengths["ld"] = float(constituency.base_ld)+ldModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif condf.columns > 0:
                    strengths["ld"] = float(constituency.base_ld)+lddf.loc[:,"ld_delta"].mean()
                else:
                    strengths["ld"] = float(constituency.base_ld)
            if constituency.base_ref != None:
                if ref:
                    strengths["ref"] = float(constituency.base_ref)+refModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif refdf.columns > 0:
                    strengths["ref"] = float(constituency.base_ref)+refdf.loc[:,"ref_delta"].mean()
                else:
                    strengths["ref"] = float(constituency.base_ref)
            if constituency.base_grn != None:
                if grn:
                    strengths["grn"] = float(constituency.base_grn)+grnModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif grndf.columns > 0:
                    strengths["grn"] = float(constituency.base_grn)+grndf.loc[:,"grn_delta"].mean()
                else:
                    strengths["grn"] = float(constituency.base_grn)
            if constituency.base_snp != None:
                if snp:
                    strengths["snp"] = float(constituency.base_snp)+snpModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif snpdf.columns > 0:
                    strengths["snp"] = float(constituency.base_snp)+snpdf.loc[:,"snp_delta"].mean()
                else:
                    strengths["snp"] = float(constituency.base_snp)
            if constituency.base_pc != None:
                if pc:
                    strengths["pc"] = float(constituency.base_pc)+pcModel([constituency.age_under_25,constituency.age_25_34,constituency.age_35_49,constituency.age_50_64,constituency.age_over_65,constituency.immigrant,constituency.white,constituency.religion_christian,constituency.religion_islam,constituency.religion_hindu,constituency.religion_other])
                elif pcdf.columns > 0:
                    strengths["pc"] = float(constituency.base_pc)+pcdf.loc[:,"pc_delta"].mean()
                else:
                    strengths["pc"] = float(constituency.base_pc)
            if constituency.base_min != None:
                strengths["min"] = float(constituency.base_min)
            detailed_projection = voteshare(strengths)
            detailed_projection['detailed'] = True
            detailed_projection['winner'] = party_capitalisations[max(detailed_projection, key=detailed_projection.get)]
            detailed_projection = Projection(**detailed_projection)
            detailed_projection.save()
            constituency.detailed_projection = detailed_projection
            constituency.save()
        updateTotals()
    except Exception as exception:
        print(exception)
        doBasicProjection()