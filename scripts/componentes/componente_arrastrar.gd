class_name ComponenteArrastrar
extends Node

@export var barra: Control
@export var objetivo: Control


func _ready() -> void:
	barra.gui_input.connect(_on_barra_input)


func _on_barra_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		objetivo.move_to_front()
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_LEFT:
		objetivo.position += event.relative
