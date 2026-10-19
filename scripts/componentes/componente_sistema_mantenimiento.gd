class_name ComponenteSistemaMantenimiento
extends Node

signal estado_cambiado

@export var nombre: String = "Sistema"
@export var consecuencia: String
@export var duracion_reinicio: float = 5.0
@export var peso_falla: float = 1.0
@export var proteccion_reparacion: float = 15.0

var fallando: bool = false
var reiniciando: bool = false
var proteccion: float = 0.0


func _process(delta: float) -> void:
	proteccion = maxf(proteccion - delta, 0.0)


func disponible_para_falla() -> bool:
	return not fallando and not reiniciando and proteccion <= 0.0


func provocar_falla() -> void:
	if not disponible_para_falla():
		return
	fallando = true
	estado_cambiado.emit()


func operativo() -> bool:
	return not fallando and not reiniciando


func comenzar_reinicio() -> void:
	reiniciando = true
	estado_cambiado.emit()


func terminar_reinicio() -> void:
	fallando = false
	reiniciando = false
	proteccion = proteccion_reparacion
	estado_cambiado.emit()


func interrumpir_reinicio() -> void:
	reiniciando = false
	estado_cambiado.emit()
