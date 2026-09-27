extends CanvasLayer
class_name PistaPopup
## PistaPopup
## Muestra el texto completo de una pista descubierta y pausa el juego
## por completo (get_tree().paused) mientras esta abierto, para que Charlie
## y todo lo demas se congele. El jugador lo cierra manualmente presionando
## la accion "interactuar" mientras esta visible.

@onready var panel: Panel = $Panel
@onready var etiqueta: Label = $Panel/Etiqueta


func _ready() -> void:
	panel.visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	SignalBus.pista_descubierta.connect(_on_pista_descubierta)


func _unhandled_input(event: InputEvent) -> void:
	if panel.visible and event.is_action_pressed("interactuar"):
		_cerrar()


func _on_pista_descubierta(pista: PistaResource) -> void:
	etiqueta.text = pista.texto
	panel.visible = true
	GameManager.ui_modal_abierta = true
	get_tree().paused = true


func _cerrar() -> void:
	panel.visible = false
	GameManager.ui_modal_abierta = false
	get_tree().paused = false

