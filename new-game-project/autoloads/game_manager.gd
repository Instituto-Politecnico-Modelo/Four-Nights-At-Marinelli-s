extends Node

enum LevelState {
	INVESTIGANDO,
	LAPTOP_DESBLOQUEADA,
	ATRAPADO,
}

var estado_actual: LevelState = LevelState.INVESTIGANDO
var ui_modal_abierta: bool = false
var charlie_escondido: bool = false

func _ready() -> void:
	SignalBus.laptop_desbloqueada.connect(_on_laptop_unlocked)
	SignalBus.charlie_atrapado.connect(_on_charlie_caught)
	SignalBus.charlie_escondido.connect(_on_charlie_escondido)


func _on_laptop_unlocked() -> void:
	estado_actual = LevelState.LAPTOP_DESBLOQUEADA

func _on_charlie_caught() -> void:
	estado_actual = LevelState.ATRAPADO

func _on_charlie_escondido(esta_escondido: bool) -> void:
	charlie_escondido = esta_escondido
