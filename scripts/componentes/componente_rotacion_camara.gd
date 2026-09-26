class_name ComponenteRotacionCamara
extends Node

@export var pivote: Node3D
@export var camara: Camera3D
@export var entrada: ComponenteEntradaMouse
@export var giro_minimo: float = -70.0
@export var giro_maximo: float = 190.0
@export var inclinacion_minima: float = -60.0
@export var inclinacion_maxima: float = 50.0


func _process(_delta: float) -> void:
	var movimiento: Vector2 = entrada.tomar_movimiento()
	pivote.rotation_degrees.y = clamp(pivote.rotation_degrees.y - movimiento.x, giro_minimo, giro_maximo)
	camara.rotation_degrees.x = clamp(camara.rotation_degrees.x - movimiento.y, inclinacion_minima, inclinacion_maxima)
