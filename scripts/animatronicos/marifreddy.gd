class_name MariFreddy
extends Node3D

signal ataque_terminado

@export var reproductor: AnimationPlayer


func _ready() -> void:
	reproductor.animation_finished.connect(_al_terminar_animacion)


func atacar() -> void:
	reproductor.play(&"ataque", 0.05)


func _al_terminar_animacion(animacion: StringName) -> void:
	if animacion == &"ataque":
		ataque_terminado.emit()
