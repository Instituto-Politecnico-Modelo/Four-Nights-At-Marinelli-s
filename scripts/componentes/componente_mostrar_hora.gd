class_name ComponenteMostrarHora
extends Node

@export var reloj: ComponenteRelojNoche
@export var etiqueta: Node
@export var digital: bool = false


func _process(_delta: float) -> void:
	if digital:
		etiqueta.text = "%d:%02d" % [reloj.hora_reloj(), reloj.minutos()]
	else:
		etiqueta.text = "%d AM" % reloj.hora_reloj()
