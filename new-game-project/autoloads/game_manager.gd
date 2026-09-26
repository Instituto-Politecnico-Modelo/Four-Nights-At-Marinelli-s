extends Node

enum LevelState {
	INVESTIGANDO,
	LAPTOP_DESBLOQUEADA,
	ATRAPADO,
}

var current_state: LevelState = LevelState.INVESTIGANDO

func _ready() -> void:
	SignalBus.laptop_unlocked.connect(_on_laptop_unlocked)
	SignalBus.charlie_caught.connect(_on_charlie_caught)


func _on_laptop_unlocked() -> void:
	current_state = LevelState.LAPTOP_DESBLOQUEADA

func _on_charlie_caught() -> void:
	current_state = LevelState.ATRAPADO
