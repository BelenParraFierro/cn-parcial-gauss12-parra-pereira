"""
Instrumentación y reporte del costo operacional.

Convención: 1 flop = 1 operación aritmética elemental en punto flotante

(+, -, *, /). Se cuentan aparte:
    mult/div  -> multiplicaciones y divisiones
    sum/res   -> sumas y restas

El sobrecosto de estabilidad (pivoteo):
    comparaciones  -> comparaciones de magnitud para elegir pivote / escala
    div_pivoteo    -> divisiones |a_ik|/s_i del pivoteo escalado
    intercambios   -> intercambios de filas efectivamente realizados
"""

from collections import OrderedDict 

CAMPOS = ("div_mult", "mult_A", "res_A", "mult_b", "res_b",
          "div_sust", "mult_sust", "res_sust",
          "comparaciones", "div_pivoteo", "intercambios")

class Contador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.fases = OrderedDict()    # un grupo de contadores por fase, en el orden en que aparecen
        self.actual = None            # la fase donde se está anotando ahora

    def fase(self, etiqueta):
        if etiqueta not in self.fases:
            self.fases[etiqueta] = dict.fromkeys(CAMPOS, 0) # todos los campos parten en 0
        self.actual = self.fases[etiqueta]

    def suma(self, campo, n=1):
        self.actual[campo] += n

    # totales
    def total(self, campo):
        return sum(f[campo] for f in self.fases.values())

    def flops_muldiv(self):
        return sum(self.total(c) for c in
                   ("div_mult", "mult_A", "mult_b", "div_sust", "mult_sust"))

    def flops_sumres(self):
        return sum(self.total(c) for c in ("res_A", "res_b", "res_sust"))

    def flops(self):
        return self.flops_muldiv() + self.flops_sumres()

    def sobrecosto(self):
        return {c: self.total(c) for c in
                ("comparaciones", "div_pivoteo", "intercambios")}

    # reporte
    def tabla_markdown(self):
        lin = []
        lin.append(f"### Corrida: {self.nombre}\n")
        lin.append("| Fase | Div. (multiplicadores) | Mult. A | Restas A "
                   "| Mult. b | Restas b | Mult/Div paso | Sum/Res paso "
                   "| Flops paso | Comparac. pivote | Div. pivote | Intercambios |")
        lin.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for et, f in self.fases.items():
            md = f["div_mult"] + f["mult_A"] + f["mult_b"] + f["div_sust"] + f["mult_sust"]
            sr = f["res_A"] + f["res_b"] + f["res_sust"]
            if et.startswith("sust"):
                lin.append(f"| {et} | div. diagonal: {f['div_sust']} | mult: {f['mult_sust']} "
                           f"| restas: {f['res_sust']} | – | – | {md} | {sr} | {md + sr} "
                           f"| {f['comparaciones']} | {f['div_pivoteo']} | {f['intercambios']} |")
            else:
                lin.append(f"| {et} | {f['div_mult']} | {f['mult_A']} | {f['res_A']} "
                           f"| {f['mult_b']} | {f['res_b']} | {md} | {sr} | {md + sr} "
                           f"| {f['comparaciones']} | {f['div_pivoteo']} | {f['intercambios']} |")
        so = self.sobrecosto()
        lin.append(f"| **Total** | {self.total('div_mult')} | {self.total('mult_A')} "
                   f"| {self.total('res_A')} | {self.total('mult_b')} | {self.total('res_b')} "
                   f"| **{self.flops_muldiv()}** | **{self.flops_sumres()}** | **{self.flops()}** "
                   f"| {so['comparaciones']} | {so['div_pivoteo']} | {so['intercambios']} |")
        lin.append("")
        lin.append(f"Flops totales (eliminación + actualización de b + sustitución regresiva): "
                   f"**{self.flops()}** = {self.flops_muldiv()} mult/div + "
                   f"{self.flops_sumres()} sum/res.  ")
        lin.append(f"Sobrecosto de estabilidad (no incluido en los flops): "
                   f"{so['comparaciones']} comparaciones, {so['div_pivoteo']} divisiones "
                   f"de pivoteo escalado, {so['intercambios']} intercambios de fila.\n")
        return "\n".join(lin)
