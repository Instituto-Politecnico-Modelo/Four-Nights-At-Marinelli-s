extends CanvasLayer
class_name PasswordInput
## PasswordInput
## Input de contrasenia para la laptop de Pruscino. Pausa el juego mientras
## esta abierto. Enter envia el intento; la accion "interactuar" (E) cierra
## el popup sin resolver el puzle.

@onready var panel: Panel = $Panel
@onready var campo: LineEdit = $Panel/VBoxContainer/Campo
@onready var etiqueta_error: Label = $Panel/VBoxContainer/EtiquetaError

var _laptop_actual: Laptop = null


func _ready() -> void:
	panel.visible = false
	etiqueta_error.visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	campo.text_submitted.connect(_on_text_submitted)
	SignalBus.laptop_abierta.connect(_on_laptop_abierta)


func _input(event: InputEvent) -> void:
	if panel.visible and event.is_action_pressed("interactuar"):
		_cerrar()
		get_viewport().set_input_as_handled()


func _on_laptop_abierta(laptop: Node) -> void:
	_laptop_actual = laptop
	campo.text = ""
	etiqueta_error.visible = false
	panel.visible = true
	GameManager.ui_modal_abierta = true
	get_tree().paused = true
	campo.grab_focus()


func _on_text_submitted(texto: String) -> void:
	if _laptop_actual == null:
		return

	if _laptop_actual.intentar_desbloquear(texto):
		var laptop := _laptop_actual
		_cerrar()
		laptop.mostrar_archivo()
	else:
		etiqueta_error.visible = true
		campo.text = ""
		campo.grab_focus()


func _cerrar() -> void:
	campo.release_focus()
	panel.visible = false
	GameManager.ui_modal_abierta = false
	get_tree().paused = false
	_laptop_actual = null
