extends CanvasLayer
class_name PantallaAtrapado
## Presentacion de la captura; GameManager coordina la pausa y el reinicio.

@onready var reintentar: Button = $Fondo/Centro/Contenido/Reintentar


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hide()
	reintentar.pressed.connect(GameManager.reiniciar)
	SignalBus.charlie_atrapado.connect(_on_charlie_atrapado)


func _on_charlie_atrapado() -> void:
	if visible:
		return
	show()
	reintentar.grab_focus()


func _input(event: InputEvent) -> void:
	# Evita que E o C lleguen a popups anteriores durante la captura.
	if visible and (event.is_action("interactuar") or event.is_action("esconderse")):
		get_viewport().set_input_as_handled()
