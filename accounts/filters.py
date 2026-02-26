import django_filters 
from django_filters import DateFilter
from django import forms
from .models import *

class DiagFilter(django_filters.FilterSet):
    start_date = DateFilter(
        field_name='date', 
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = DateFilter(
        field_name='date', 
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    class Meta:
        model = PatientHasDiagnosis
        fields = ['date', 'diagnosis', 'start_date', 'end_date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class PatientFilter(django_filters.FilterSet):
    class Meta:
        model = Patient
        # fields = '__all__'
        fields = ['id','name', 'surname']