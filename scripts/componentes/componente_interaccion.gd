class_name ComponenteInteraccion
extends Node

@export var rayo: RayCast3D

var objetivo: ComponenteInteractuable = null


func _process(_delta: float) -> void:
	var nuevo: ComponenteInteractuable = null
	if rayo.is_colliding():
		nuevo = rayo.get_collider() as ComponenteInteractuable

	if objetivo != null and objetivo != nuevo:
		objetivo.presionado = false

	objetivo = nuevo
	if objetivo != null:
		objetivo.presionado = Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)
