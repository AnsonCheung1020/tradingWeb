from django import forms 

class StockScreenerForm (forms.Form):
    search_period=forms.IntegerField(label='Enter the searching period (in days >=0)', min_value=0)