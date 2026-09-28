extends Node

enum LevelState {
	INVESTIGANDO,
	LAPTOP_DESBLOQUEADA,
	ATRAPADO,
}

var estado_actual: LevelState = LevelState.INVESTIGANDO
var ui_modal_abierta: bool = false
var charlie_escondido: bool = false
var _reiniciando: bool = false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	SignalBus.laptop_desbloqueada.connect(_on_laptop_unlocked)
	SignalBus.charlie_atrapado.connect(_on_charlie_caught)
	SignalBus.charlie_escondido.connect(_on_charlie_escondido)


func _on_laptop_unlocked() -> void:
	if _reiniciando or estado_actual == LevelState.ATRAPADO:
		return
	estado_actual = LevelState.LAPTOP_DESBLOQUEADA

func _on_charlie_caught() -> void:
	if _reiniciando or estado_actual == LevelState.ATRAPADO:
		return
	estado_actual = LevelState.ATRAPADO
	ui_modal_abierta = true
	get_tree().paused = true

func _on_charlie_escondido(esta_escondido: bool) -> void:
	if _reiniciando:
		return
	charlie_escondido = esta_escondido


func _input(event: InputEvent) -> void:
	# Se procesa antes de los controles de texto, incluso durante la pausa.
	if event.is_action_pressed("reiniciar_nivel"):
		get_viewport().set_input_as_handled()
		reiniciar()


func reiniciar() -> void:
	if _reiniciando or get_tree().current_scene == null:
		return
	_reiniciando = true
	# La captura puede originarse en fisica; recargar fuera de ese callback.
	_recargar_nivel.call_deferred()


func _recargar_nivel() -> void:
	var estado_anterior := estado_actual
	var modal_anterior := ui_modal_abierta
	var escondido_anterior := charlie_escondido
	var pausa_anterior := get_tree().paused
	get_tree().paused = true
	estado_actual = LevelState.INVESTIGANDO
	ui_modal_abierta = false
	charlie_escondido = false
	var error := get_tree().reload_current_scene()
	if error != OK:
		estado_actual = estado_anterior
		ui_modal_abierta = modal_anterior
		charlie_escondido = escondido_anterior
		get_tree().paused = pausa_anterior
		_reiniciando = false
		push_error("No se pudo reiniciar el nivel: %s" % error_string(error))
		return
	await get_tree().scene_changed
	get_tree().paused = false
	_reiniciando = false
