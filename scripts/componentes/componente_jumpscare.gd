class_name ComponenteJumpscare
extends Node

signal jumpscare_terminado

@export var animatronico: Pruscino
@export var vigilancia: ComponenteVigilanciaVentana
@export var punto: Marker3D
@export var sonido: AudioStreamPlayer3D

var rotacion: ComponenteRotacionCamara


func _ready() -> void:
	rotacion = get_tree().get_first_node_in_group("rotacion_camara")
	vigilancia.jumpscare_solicitado.connect(_al_solicitar)
	animatronico.ataque_terminado.connect(jumpscare_terminado.emit)


func _al_solicitar() -> void:
	rotacion.set_process(false)
	rotacion.pivote.rotation_degrees.y = 90.0
	rotacion.camara.rotation_degrees.x = 0.0
	animatronico.global_transform = punto.global_transform
	animatronico.atacar()
	sonido.play()
