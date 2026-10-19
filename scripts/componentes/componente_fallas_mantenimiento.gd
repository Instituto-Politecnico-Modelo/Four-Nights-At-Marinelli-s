class_name ComponenteFallasMantenimiento
extends Node

@export var sistemas: Array[ComponenteSistemaMantenimiento] = []
@export var reloj: ComponenteRelojNoche
@export var primera_falla: Vector2 = Vector2(25.0, 35.0)
@export var intervalo_inicial: Vector2 = Vector2(35.0, 50.0)
@export var intervalo_final: Vector2 = Vector2(20.0, 30.0)

var tiempo: float = 0.0


func _ready() -> void:
	tiempo = randf_range(primera_falla.x, primera_falla.y)


func _process(delta: float) -> void:
	if reloj.terminada:
		return
	tiempo -= delta
	if tiempo > 0.0:
		return
	provocar_incidente()
	var avance: float = clampf(float(reloj.hora) / maxf(reloj.horas_totales - 1, 1), 0.0, 1.0)
	var intervalo: Vector2 = intervalo_inicial.lerp(intervalo_final, avance)
	tiempo = randf_range(intervalo.x, intervalo.y)


func provocar_incidente() -> void:
	var disponibles: Array[ComponenteSistemaMantenimiento] = []
	var peso_total: float = 0.0
	for sistema in sistemas:
		if sistema.disponible_para_falla():
			disponibles.append(sistema)
			peso_total += maxf(sistema.peso_falla, 0.0)
	if peso_total <= 0.0:
		return
	var seleccion: float = randf() * peso_total
	for sistema in disponibles:
		seleccion -= maxf(sistema.peso_falla, 0.0)
		if seleccion <= 0.0:
			sistema.provocar_falla()
			return
