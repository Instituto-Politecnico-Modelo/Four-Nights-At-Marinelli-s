class_name ComponenteEstadosAparicion
extends Node

signal estado_cambiado(indice: int)

@export var objetivo: Pruscino

var estados: Array[EstadoAparicion] = []
var indice: int = 0


func _ready() -> void:
	for hijo in get_children():
		if hijo is EstadoAparicion:
			estados.append(hijo)
	ir_a(0)


func avanzar() -> void:
	ir_a(indice + 1)


func retroceder() -> void:
	ir_a(indice - 1)


func ir_a(nuevo: int) -> void:
	indice = clampi(nuevo, 0, estados.size() - 1)
	var estado: EstadoAparicion = estados[indice]
	objetivo.visible = not estado.oculto
	objetivo.global_transform = estado.global_transform
	objetivo.reproducir(estado.animacion)
	estado_cambiado.emit(indice)
