from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
    chart_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    chart_ea_nsp = [10, 12, 15, 8, 20, 15, 10, 14, 18, 12, 10, 10]
    chart_ea_notivisa = [2, 3, 5, 2, 6, 4, 2, 5, 4, 3, 3, 3]
    chart_ea_queda = [1, 0, 2, 1, 0, 1, 2, 1, 0, 2, 1, 1]
    chart_ea_flebite = [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0]

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
        "chart_labels": chart_labels,
        "chart_ea_nsp": chart_ea_nsp,
        "chart_ea_notivisa": chart_ea_notivisa,
        "chart_ea_queda": chart_ea_queda,
        "chart_ea_flebite": chart_ea_flebite,
    }

    context = {
        "titulo": "Dashboard NSP - Seguranca do Paciente",
        "stats": stats,
        "chart_data": chart_data,
        "anos": [2023, 2024, 2025],
        "ano_selecionado": 2024,
        "setores": ["UTI Adulto", "Emergencia", "Centro Cirurgico", "Clinica Medica"],
    }
    return render(request, "nsp/dashboard.html", context)
