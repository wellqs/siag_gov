from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import redirect, render
from django.utils import timezone

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
    base_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    chart_data = {
        "chart_labels": base_labels,
        "chart_ea_nsp": [0] * 12,
        "chart_ea_notivisa": [0] * 12,
        "chart_ea_queda": [0] * 12,
        "chart_ea_flebite": [0] * 12,
    }
    stats = {
        "total_ea_nsp": 0,
        "total_ea_notivisa": 0,
        "taxa_conformidade": 0,
        "total_pacientes": 0,
        "total_pulseiras": 0,
        "total_ea_queda": 0,
        "total_ea_flebite": 0,
    }

    latest_ref = MetricEntry.objects.order_by("-referencia").first()
    ano_selecionado = int(
        request.GET.get("ano")
        or (latest_ref.referencia.year if latest_ref else timezone.now().year)
    )
    mes_param = request.GET.get("mes")
    try:
        mes_selecionado = int(mes_param) if mes_param else (latest_ref.referencia.month if latest_ref else 1)
    except (TypeError, ValueError):
        mes_selecionado = 1

    qs_year = MetricEntry.objects.filter(referencia__year=ano_selecionado)
    monthly = (
        qs_year.annotate(month=ExtractMonth("referencia"))
        .values("month")
        .annotate(
            ea_nsp=Sum("total_ea_nsp"),
            ea_notivisa=Sum("total_ea_notivisa"),
            queda=Sum("total_ea_queda"),
            flebite=Sum("total_ea_flebite"),
            pulseiras=Sum("total_pulseiras"),
            pacientes=Sum("total_pacientes"),
        )
        .order_by("month")
    )

    monthly_map = {row["month"]: row for row in monthly}
    for row in monthly:
        idx = row["month"] - 1
        chart_data["chart_ea_nsp"][idx] = row["ea_nsp"] or 0
        chart_data["chart_ea_notivisa"][idx] = row["ea_notivisa"] or 0
        chart_data["chart_ea_queda"][idx] = row["queda"] or 0
        chart_data["chart_ea_flebite"][idx] = row["flebite"] or 0

    if mes_param:
        # Zera meses fora do filtro para refletir apenas o mes escolhido no grafico
        filtered = {"chart_ea_nsp": [0] * 12, "chart_ea_notivisa": [0] * 12, "chart_ea_queda": [0] * 12, "chart_ea_flebite": [0] * 12}
        row = monthly_map.get(mes_selecionado)
        if row:
            idx = mes_selecionado - 1
            filtered["chart_ea_nsp"][idx] = row["ea_nsp"] or 0
            filtered["chart_ea_notivisa"][idx] = row["ea_notivisa"] or 0
            filtered["chart_ea_queda"][idx] = row["queda"] or 0
            filtered["chart_ea_flebite"][idx] = row["flebite"] or 0
        chart_data.update(filtered)

    # Cards: usa agregacao do mes selecionado (ou zero se nao existir)
    if qs_year.exists():
        month_agg = qs_year.filter(referencia__month=mes_selecionado).aggregate(
            ea_nsp=Sum("total_ea_nsp"),
            ea_notivisa=Sum("total_ea_notivisa"),
            queda=Sum("total_ea_queda"),
            flebite=Sum("total_ea_flebite"),
            pulseiras=Sum("total_pulseiras"),
            pacientes=Sum("total_pacientes"),
        )
        total_pacientes = month_agg["pacientes"] or 0
        total_pulseiras = month_agg["pulseiras"] or 0
        taxa_conf = 0
        if total_pacientes:
            taxa_conf = float((total_pulseiras / total_pacientes) * 100)
        stats = {
            "total_ea_nsp": month_agg["ea_nsp"] or 0,
            "total_ea_notivisa": month_agg["ea_notivisa"] or 0,
            "taxa_conformidade": round(taxa_conf, 2),
            "total_pacientes": total_pacientes,
            "total_pulseiras": total_pulseiras,
            "total_ea_queda": month_agg["queda"] or 0,
            "total_ea_flebite": month_agg["flebite"] or 0,
        }

    anos_disponiveis = set(MetricEntry.objects.values_list("referencia__year", flat=True))
    anos_disponiveis.update({2023, 2024, 2025, ano_selecionado})

    context = {
        "titulo": "Dashboard NSP - Seguranca do Paciente",
        "stats": stats,
        "chart_data": chart_data,
        "anos": sorted(anos_disponiveis),
        "ano_selecionado": ano_selecionado,
        "meses": [
            (1, "Jan"), (2, "Fev"), (3, "Mar"), (4, "Abr"), (5, "Mai"), (6, "Jun"),
            (7, "Jul"), (8, "Ago"), (9, "Set"), (10, "Out"), (11, "Nov"), (12, "Dez")
        ],
        "mes_selecionado": mes_selecionado,
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


def logout_view(request):
    """Encerrar sessao e redirecionar para a tela de login."""
    logout(request)
    return redirect("login")


@login_required
def equipe(request):
    """Pagina estatica para listar equipe do NSP/gestao."""
    members = [
        {"nome": "LEIDIANE DA SILVA SANTANA", "cargo": "Cordenadora NSP", "email": "nsphc.ro@gmail.com"},
        {"nome": "NARJARA LOPES DA SILVA", "cargo": "Auxiliar Tecnica", "email": "nsphc.ro@gmail.com"},
    ]
    return render(request, "nsp/equipe.html", {"members": members})
