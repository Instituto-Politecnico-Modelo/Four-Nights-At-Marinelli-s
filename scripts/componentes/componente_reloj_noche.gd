class_name ComponenteRelojNoche
extends Node

signal hora_cambiada(hora: int)
signal noche_terminada

@export var segundos_por_hora: float = 90.0
@export var horas_totales: int = 6

var tiempo: float = 0.0
var hora: int = 0
var terminada: bool = false


func _process(delta: float) -> void:
	if terminada:
		return

	tiempo += delta
	var nueva_hora: int = int(tiempo / segundos_por_hora)
	if nueva_hora != hora:
		hora = nueva_hora
		hora_cambiada.emit(hora)
		if hora >= horas_totales:
			terminada = true
			noche_terminada.emit()


func restaurar(hora_inicio: int) -> void:
	hora = clampi(hora_inicio, 0, horas_totales)
	tiempo = float(hora) * segundos_por_hora
	if hora >= horas_totales:
		terminada = true
	hora_cambiada.emit(hora)


func hora_reloj() -> int:
	if hora == 0:
		return 12
	return hora


func minutos() -> int:
	if terminada:
		return 0
	return int(fmod(tiempo, segundos_por_hora) / segundos_por_hora * 60.0)
