class_name Pruscino
extends Node3D

signal ataque_terminado

@export var reproductor: AnimationPlayer
@export var tiempo_mezcla: float = 0.25


func _ready() -> void:
	reproductor.animation_finished.connect(_al_terminar_animacion)


func reproducir(animacion: StringName) -> void:
	reproductor.play(animacion, tiempo_mezcla)


func atacar() -> void:
	reproductor.play(&"ataque", 0.05)


func _al_terminar_animacion(animacion: StringName) -> void:
	if animacion == &"ataque":
		ataque_terminado.emit()
