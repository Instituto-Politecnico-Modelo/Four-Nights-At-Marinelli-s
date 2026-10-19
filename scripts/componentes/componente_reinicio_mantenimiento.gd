class_name ComponenteReinicioMantenimiento
extends Node

signal estado_cambiado

@export var sistemas: Array[ComponenteSistemaMantenimiento] = []
@export var reloj: ComponenteRelojNoche
@export var duracion_conjunta: float = 12.0

var afectados: Array[ComponenteSistemaMantenimiento] = []
var tiempo: float = 0.0
var duracion: float = 0.0


func _ready() -> void:
	reloj.noche_terminada.connect(interrumpir)


func _process(delta: float) -> void:
	if not activo():
		return
	tiempo = minf(tiempo + delta, duracion)
	if tiempo < duracion:
		return
	for sistema in afectados:
		sistema.terminar_reinicio()
	afectados.clear()
	estado_cambiado.emit()


func activo() -> bool:
	return not afectados.is_empty()


func iniciar(sistema: ComponenteSistemaMantenimiento = null) -> bool:
	if activo() or reloj.terminada:
		return false
	if sistema != null:
		if not sistemas.has(sistema) or not sistema.fallando:
			return false
		afectados.append(sistema)
		duracion = sistema.duracion_reinicio
	else:
		for candidato in sistemas:
			if candidato.fallando:
				afectados.append(candidato)
		duracion = duracion_conjunta
	if afectados.is_empty():
		return false
	tiempo = 0.0
	for afectado in afectados:
		afectado.comenzar_reinicio()
	estado_cambiado.emit()
	return true


func interrumpir() -> void:
	if not activo():
		return
	for sistema in afectados:
		sistema.interrumpir_reinicio()
	afectados.clear()
	tiempo = 0.0
	estado_cambiado.emit()
