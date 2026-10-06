class_name ComponenteInterferenciaCamaras
extends Node

@export var estados: ComponenteEstadosAparicion
@export var duracion: float = 4.0

var tiempo_restante: float = 0.0


func _ready() -> void:
	estados.estado_cambiado.connect(_al_cambiar_estado)


func _process(delta: float) -> void:
	tiempo_restante = maxf(tiempo_restante - delta, 0.0)


func apagada() -> bool:
	return tiempo_restante > 0.0


func _al_cambiar_estado(_indice: int) -> void:
	tiempo_restante = duracion
