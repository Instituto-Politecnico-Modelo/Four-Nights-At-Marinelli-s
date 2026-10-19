class_name ComponenteAbrirVentana
extends Node

@export var boton: Control
@export var ventana: Control
@export var menu: Control
@export var doble_click: bool = false


func _ready() -> void:
	boton.gui_input.connect(_on_boton_input)


func _on_boton_input(event: InputEvent) -> void:
	if not event is InputEventMouseButton:
		return
	if not event.pressed or event.button_index != MOUSE_BUTTON_LEFT:
		return
	if doble_click and not event.double_click:
		return
	var reinicio: ComponenteReinicioMantenimiento = get_tree().get_first_node_in_group("reinicio_mantenimiento") as ComponenteReinicioMantenimiento
	if reinicio != null and reinicio.activo():
		return

	ventana.show()
	ventana.move_to_front()
	if menu != null:
		menu.hide()
