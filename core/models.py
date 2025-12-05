from django.db import models
from django.utils import timezone


class Example(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class MetricEntry(models.Model):
    referencia = models.DateField(default=timezone.now)
    total_ea_nsp = models.PositiveIntegerField()
    total_ea_notivisa = models.PositiveIntegerField()
    total_pulseiras = models.PositiveIntegerField()
    total_ea_queda = models.PositiveIntegerField()
    total_ea_flebite = models.PositiveIntegerField()
    taxa_conformidade = models.DecimalField(max_digits=5, decimal_places=2)
    total_pacientes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Metricas {self.referencia} ({self.total_ea_nsp} NSP)"
