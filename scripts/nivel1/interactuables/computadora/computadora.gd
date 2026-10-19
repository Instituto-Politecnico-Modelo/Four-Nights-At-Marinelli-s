extends Node2D
class_name Computadora

@export var pista: PistaResource

@onready var interactuable: InteractableComponent = $InteractableComponent


func _ready() -> void:
	interactuable.interactuado.connect(_on_interactuado)


func _on_interactuado() -> void:
	if pista != null:
		SignalBus.pista_descubierta.emit(pista)
