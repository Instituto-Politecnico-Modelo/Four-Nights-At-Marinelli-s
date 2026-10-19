class_name ComponenteAvisoMantenimiento
extends Node

@export var reinicio: ComponenteReinicioMantenimiento
@export var etiqueta: Label


func _ready() -> void:
	for sistema in reinicio.sistemas:
		sistema.estado_cambiado.connect(_actualizar)
	reinicio.reloj.noche_terminada.connect(_actualizar)
	_actualizar()


func _actualizar() -> void:
	var fallas: PackedStringArray = []
	for sistema in reinicio.sistemas:
		if sistema.fallando:
			fallas.append(sistema.nombre)
	etiqueta.visible = not fallas.is_empty() and not reinicio.reloj.terminada
	etiqueta.text = "ERROR: %s\nAccedé a Mantenimiento en la computadora." % ", ".join(fallas)
