class_name ComponenteParpadeo
extends Node

@export var objetivo: CanvasItem
@export var intervalo: float = 0.6

var tiempo: float = 0.0


func _process(delta: float) -> void:
	tiempo += delta
	if tiempo >= intervalo:
		tiempo = 0.0
		objetivo.visible = not objetivo.visible
