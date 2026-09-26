class_name EscritorioXP
extends Control

signal apagado

@export var fondo: Control
@export var menu_inicio: Control
@export var boton_inicio: Button
@export var boton_apagar: Button


func _ready() -> void:
	menu_inicio.hide()
	boton_inicio.pressed.connect(_alternar_menu)
	boton_apagar.pressed.connect(_apagar)
	fondo.gui_input.connect(_on_fondo_input)


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		_apagar()


func _alternar_menu() -> void:
	menu_inicio.visible = not menu_inicio.visible
	menu_inicio.move_to_front()


func _on_fondo_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		menu_inicio.hide()


func _apagar() -> void:
	menu_inicio.hide()
	apagado.emit()
