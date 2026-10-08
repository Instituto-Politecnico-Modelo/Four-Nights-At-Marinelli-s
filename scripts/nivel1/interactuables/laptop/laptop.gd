extends Node2D
class_name Laptop
## Laptop
## Guarda el desbloqueo del intento actual y permite releer el archivo.

@export var contrasenia_correcta: String = "1409"
@export var archivo_secreto: PistaResource = preload("res://resources/nivel1/pistas/archivo_secreto.tres")

var desbloqueada: bool = false

@onready var interactuable: InteractableComponent = $InteractableComponent


func _ready() -> void:
	interactuable.interactuado.connect(_on_interactuado)


func _on_interactuado() -> void:
	if desbloqueada:
		mostrar_archivo()
	else:
		SignalBus.laptop_abierta.emit(self)


func intentar_desbloquear(texto: String) -> bool:
	if desbloqueada:
		return true
	if texto.strip_edges() != contrasenia_correcta.strip_edges():
		SignalBus.intento_contrasenia_fallido.emit()
		return false
	desbloqueada = true
	SignalBus.laptop_desbloqueada.emit()
	return true


func mostrar_archivo() -> void:
	if desbloqueada and archivo_secreto != null:
		SignalBus.pista_descubierta.emit(archivo_secreto)
