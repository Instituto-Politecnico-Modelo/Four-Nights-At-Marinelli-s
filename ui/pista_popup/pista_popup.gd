extends CanvasLayer
class_name PistaPopup

@onready var panel: Panel = $Panel
@onready var etiqueta: Label = $Panel/Etiqueta


func _ready() -> void:
	panel.visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	SignalBus.pista_descubierta.connect(_on_pista_descubierta)


func _input(event: InputEvent) -> void:
	if panel.visible and event.is_action_pressed("interactuar"):
		_cerrar()
		get_viewport().set_input_as_handled()


func _on_pista_descubierta(pista: PistaResource) -> void:
	show()
	etiqueta.text = pista.texto + "\n\n[E] Cerrar"
	panel.visible = true
	GameManager.ui_modal_abierta = true
	get_tree().paused = true


func _cerrar() -> void:
	panel.visible = false
	GameManager.ui_modal_abierta = false
	get_tree().paused = false
