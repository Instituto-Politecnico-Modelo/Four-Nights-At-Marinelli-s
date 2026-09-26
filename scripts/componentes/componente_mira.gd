class_name ComponenteMira
extends Control

@export var interaccion: ComponenteInteraccion
@export var radio_normal: float = 2.5
@export var radio_interactuable: float = 8.0
@export var velocidad: float = 60.0
@export var color: Color = Color(1, 1, 1, 0.85)

var radio: float = 2.5


func _process(delta: float) -> void:
	var objetivo: float = radio_normal
	if interaccion.objetivo != null:
		objetivo = radio_interactuable

	radio = move_toward(radio, objetivo, velocidad * delta)
	queue_redraw()


func _draw() -> void:
	draw_circle(Vector2.ZERO, radio, color, true, -1.0, true)
