class_name ComponentePersiana
extends Node

@export var interactuable: ComponenteInteractuable
@export var tela: Node3D
@export var escala_abierta: float = 0.08
@export var escala_cerrada: float = 1.0
@export var velocidad: float = 1.5

var cerrada: bool = false
var cerrando: bool = false


func _process(delta: float) -> void:
	var presionado: bool = interactuable.presionado
	if presionado and not cerrando:
		Sonidos.persiana()
	cerrando = presionado

	var objetivo: float = escala_abierta
	if presionado:
		objetivo = escala_cerrada

	tela.scale.y = move_toward(tela.scale.y, objetivo, velocidad * delta)
	cerrada = tela.scale.y == escala_cerrada
