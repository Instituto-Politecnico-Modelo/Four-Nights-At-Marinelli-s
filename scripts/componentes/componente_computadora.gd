class_name ComponenteComputadora
extends Node

@export var interactuable: ComponenteInteractuable
@export var escritorio: EscritorioXP
@export var jugador: Node

var presionado_antes: bool = false


func _ready() -> void:
	escritorio.hide()
	escritorio.apagado.connect(cerrar)


func _process(_delta: float) -> void:
	if interactuable.presionado and not presionado_antes:
		abrir()
	presionado_antes = interactuable.presionado


func abrir() -> void:
	escritorio.show()
	jugador.process_mode = Node.PROCESS_MODE_DISABLED
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func cerrar() -> void:
	escritorio.hide()
	jugador.process_mode = Node.PROCESS_MODE_INHERIT
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
