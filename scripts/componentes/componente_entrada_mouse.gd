class_name ComponenteEntradaMouse
extends Node

@export var sensibilidad: float = 0.15

var movimiento: Vector2 = Vector2.ZERO


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		movimiento += event.relative * sensibilidad
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func tomar_movimiento() -> Vector2:
	var valor: Vector2 = movimiento
	movimiento = Vector2.ZERO
	return valor
