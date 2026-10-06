class_name Pruscino
extends Node3D

## Animatronico Pruscino (Bonnie de FNAF 1 fusionado con Pruscino).
## El modelo importado mira hacia +Z (convencion de glTF); la escena lo gira 180 grados
## para que "adelante" sea -Z, como en el resto del proyecto.

signal ataque_terminado

@export var reproductor: AnimationPlayer
@export var tiempo_mezcla: float = 0.25
@export var velocidad_caminata: float = 1.3

var atacando: bool = false


func _ready() -> void:
	reproductor.animation_finished.connect(_al_terminar_animacion)
	reproducir_idle()


func reproducir_idle() -> void:
	if atacando:
		return
	reproductor.play("idle", tiempo_mezcla)


func caminar() -> void:
	if atacando:
		return
	reproductor.play("caminar", tiempo_mezcla)


## Jumpscare. La animacion es "en sitio": acerca el nodo a la camara desde afuera si hace falta.
func atacar() -> void:
	atacando = true
	reproductor.play("ataque", 0.05)
	Sonidos.jumpscare_prusbonnie()


## Camina hacia adelante (-Z local) mientras suena la animacion de caminata.
func avanzar(delta: float) -> void:
	caminar()
	translate(Vector3(0.0, 0.0, -velocidad_caminata * delta))


func _al_terminar_animacion(nombre: StringName) -> void:
	if nombre == &"ataque":
		ataque_terminado.emit()
