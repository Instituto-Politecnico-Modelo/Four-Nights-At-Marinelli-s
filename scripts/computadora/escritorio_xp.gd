class_name EscritorioXP
extends Control

signal apagado

@export var fondo: Control
@export var menu_inicio: Control
@export var boton_inicio: Button
@export var boton_apagar: Button
@export var ventana_mantenimiento: Control
@export var bloqueo_mantenimiento: Control

var reinicio: ComponenteReinicioMantenimiento


func _ready() -> void:
	menu_inicio.hide()
	boton_inicio.pressed.connect(_alternar_menu)
	boton_apagar.pressed.connect(_apagar)
	fondo.gui_input.connect(_on_fondo_input)
	reinicio = get_tree().get_first_node_in_group("reinicio_mantenimiento") as ComponenteReinicioMantenimiento
	if reinicio != null:
		reinicio.estado_cambiado.connect(_actualizar_bloqueo)
	_actualizar_bloqueo()


func _input(event: InputEvent) -> void:
	if is_visible_in_tree() and event.is_action_pressed("ui_cancel"):
		_apagar()
		get_viewport().set_input_as_handled()


func _actualizar_bloqueo() -> void:
	if bloqueo_mantenimiento == null:
		return
	bloqueo_mantenimiento.visible = reinicio != null and reinicio.activo()
	if bloqueo_mantenimiento.visible:
		menu_inicio.hide()
		bloqueo_mantenimiento.move_to_front()
		ventana_mantenimiento.show()
		ventana_mantenimiento.move_to_front()


func _alternar_menu() -> void:
	if reinicio != null and reinicio.activo():
		return
	menu_inicio.visible = not menu_inicio.visible
	menu_inicio.move_to_front()


func _on_fondo_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		menu_inicio.hide()


func _apagar() -> void:
	menu_inicio.hide()
	if reinicio != null:
		reinicio.interrumpir()
	apagado.emit()
