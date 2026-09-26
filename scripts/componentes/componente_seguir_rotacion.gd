class_name ComponenteSeguirRotacion
extends Node

@export var origen: Node3D
@export var destino: Node3D


func _process(_delta: float) -> void:
	destino.global_rotation.y = origen.global_rotation.y
