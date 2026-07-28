from django import forms

class EMA821Form(forms.Form):
    search_period=forms.IntegerField(label="Enter the searching period (days >= 0)", min_value=0)