from django.db import models

class Parties(models.TextChoices):
    CON = 'Con', 'Conservative and Unionist Party'
    LAB = 'Lab', 'Labour Party'
    LD = 'LD', 'Liberal Democrats'
    SNP = 'SNP', 'Scottish National Party'
    GRN = 'Grn', 'Green Party'
    REF = 'Ref', 'Reform UK'
    PC = 'PC', 'Plaid Cymru'
    WPB = 'WPB', 'Workers Party of Britain'
    SDP = 'SDP', 'Social Democratic Party'
    UKIP = 'UKIP', 'UK Independence Party'
    ALBA = 'Alba', 'Alba Party'
    IND = 'Ind', 'Independent'
    OTH = 'Oth', 'Other'


class Constituency(models.Model):
    class Regions(models.TextChoices):
        NORTH_EAST = 'NE','North East'
        NORTH_WEST = 'NW','North West'
        YORKSHIRE = 'Y','Yorkshire and the Humber'
        WEST_MIDLANDS = 'WM','West Midlands'
        EAST_MIDLANDS = 'EM','East Midlands'
        SOUTH_WEST = 'SW','South West'
        SOUTH_EAST = 'SE','South East'
        LONDON = 'L','London'
        EAST = 'E','East of England'
        SCOTLAND = 'S','Scotland'
        WALES = 'W','Wales'
    
    name = models.CharField(max_length=64, unique=True, verbose_name='Constituency Name')
    id = models.CharField(max_length=9, primary_key=True)
    region = models.CharField(max_length=2, choices=Regions.choices, verbose_name='Region')
    winner2019 = models.CharField(max_length=4, choices=Parties.choices, verbose_name='2019 Winner')

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'constituency'
        verbose_name_plural = 'constituencies'