extends Node2D
class_name Laptop
## Laptop
## La laptop de Pruscino. Al interactuar, no valida la contrasenia ella misma:
## le avisa a la UI (PasswordInput) que se abra, pasandose a si misma para
## que esta pueda comparar contra su propia contrasenia_correcta.

@export var contrasenia_correcta: String = "1984"

@onready var interactuable: InteractableComponent = $InteractableComponent


func _ready() -> void:
	interactuable.interactuado.connect(_on_interactuado)


func _on_interactuado() -> void:
	SignalBus.laptop_abierta.emit(self)
