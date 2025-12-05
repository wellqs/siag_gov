from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import MetricEntry


class MetricEntryForm(forms.ModelForm):
    class Meta:
        model = MetricEntry
        fields = [
            "referencia",
            "total_ea_nsp",
            "total_ea_notivisa",
            "total_pulseiras",
            "total_ea_queda",
            "total_ea_flebite",
            "taxa_conformidade",
            "total_pacientes",
        ]
        widgets = {
            "referencia": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "total_ea_nsp": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "total_ea_notivisa": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "total_pulseiras": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "total_ea_queda": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "total_ea_flebite": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "taxa_conformidade": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0, "max": 100}),
            "total_pacientes": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
        labels = {
            "referencia": "Data de referencia",
            "total_ea_nsp": "Numero de EA ao NSP",
            "total_ea_notivisa": "Numero de EA NOTIVISA",
            "total_pulseiras": "Pacientes com pulseiras padronizadas",
            "total_ea_queda": "Numero de eventos de queda",
            "total_ea_flebite": "Eventos por flebite",
            "taxa_conformidade": "Taxa de conformidade (%)",
            "total_pacientes": "Total de pacientes avaliados",
        }


@login_required
def home(request):
    user_display = request.user.first_name or request.user.username or "Usuario"
    context = {
        "user_display": user_display,
        "user_role": "Coordenador NSP",
    }
    return render(request, "nsp/home.html", context)


@login_required
def dashboard(request):
    latest = MetricEntry.objects.order_by("-created_at").first()
    if latest:
        stats = {
            "total_ea_nsp": latest.total_ea_nsp,
            "total_ea_notivisa": latest.total_ea_notivisa,
            "taxa_conformidade": float(latest.taxa_conformidade),
            "total_pacientes": latest.total_pacientes,
            "total_pulseiras": latest.total_pulseiras,
            "total_ea_queda": latest.total_ea_queda,
            "total_ea_flebite": latest.total_ea_flebite,
        }
        base_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        chart_data = {
            "chart_labels": base_labels,
            "chart_ea_nsp": [latest.total_ea_nsp] * 12,
            "chart_ea_notivisa": [latest.total_ea_notivisa] * 12,
            "chart_ea_queda": [latest.total_ea_queda] * 12,
            "chart_ea_flebite": [latest.total_ea_flebite] * 12,
        }
        ano = latest.referencia.year
    else:
        stats = {
            "total_ea_nsp": 154,
            "total_ea_notivisa": 42,
            "taxa_conformidade": 92.5,
            "total_pacientes": 1250,
            "total_pulseiras": 1156,
            "total_ea_queda": 12,
            "total_ea_flebite": 5,
        }
        chart_data = {
            "chart_labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
            "chart_ea_nsp": [10, 12, 15, 8, 20, 15, 10, 14, 18, 12, 10, 10],
            "chart_ea_notivisa": [2, 3, 5, 2, 6, 4, 2, 5, 4, 3, 3, 3],
            "chart_ea_queda": [1, 0, 2, 1, 0, 1, 2, 1, 0, 2, 1, 1],
            "chart_ea_flebite": [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        }
        ano = 2024

    chart_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    chart_data.setdefault("chart_labels", chart_labels)

    context = {
        "titulo": "Dashboard NSP - Seguranca do Paciente",
        "stats": stats,
        "chart_data": chart_data,
        "anos": [2023, 2024, 2025],
        "ano_selecionado": ano,
        "setores": ["UTI Adulto", "Emergencia", "Centro Cirurgico", "Clinica Medica"],
    }
    return render(request, "nsp/dashboard.html", context)


@login_required
def coleta(request):
    if request.method == "POST":
        form = MetricEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = MetricEntryForm()
    return render(request, "nsp/coleta.html", {"form": form})
