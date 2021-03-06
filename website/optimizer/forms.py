from django import forms
import os
from pathlib import Path

CHOICES=[('not_random','Not Random'),
         ('uniform','Uniform'),
         ('gaussian', 'Gaussian')]

def get_slates():
    slate_files = os.listdir(Path(r'//home/ubuntu/Fantasy-Fire/website/optimizer/Slates'))
    slates = []
    for slate in slate_files:
        if "Main" in slate:
            slates.insert(0, (slate[:-4], slate[:-4]))
        elif "Night" in slate:
            slates.insert(2, (slate[:-4], slate[:-4]))
        elif "Turbo" in slate:
            slates.insert(1, (slate[:-4], slate[:-4]))
        else:
            slates.append((slate[:-4], slate[:-4]))
    return slates



class OptimizerForm(forms.Form):
    no_lineups = forms.IntegerField(label='Number of Lineups', min_value=1, initial=1)
    # min_deviation = forms.DecimalField(label='Minimum Deviation %', min_value=0, initial=0)
    deviation = forms.DecimalField(label='Deviation %', min_value=0, initial=15)
    min_salary = forms.IntegerField(label='Minimum Salary', max_value=50000, min_value=15000, initial=40000)
    max_exposure = forms.IntegerField(label='Maximum Exposure', max_value=100, min_value=1, initial=100)
    generation_type = forms.ChoiceField(choices=CHOICES)
    with_replacement = forms.BooleanField(required=False)


class SlateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slate'].initial = 'override'

    slate = forms.ChoiceField(choices=get_slates())
