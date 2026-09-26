class_name ComponenteBisagra
extends Node

@export var interactuable: ComponenteInteractuable
@export var bisagra: Node3D
@export var angulo_abierto: float = -95.0
@export var angulo_cerrado: float = 0.0
@export var velocidad: float = 300.0

var cerrada: bool = false


func _process(delta: float) -> void:
	var objetivo: float = angulo_abierto
	if interactuable.presionado:
		objetivo = angulo_cerrado

	bisagra.rotation_degrees.y = move_toward(bisagra.rotation_degrees.y, objetivo, velocidad * delta)
	cerrada = bisagra.rotation_degrees.y == angulo_cerrado
