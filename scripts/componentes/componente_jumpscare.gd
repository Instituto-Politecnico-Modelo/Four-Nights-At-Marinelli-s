class_name ComponenteJumpscare
extends Node

signal jumpscare_terminado

@export var animatronico: Node3D
@export var punto: Marker3D
@export var sonido: AudioStreamPlayer3D
@export var angulo_mirada: float = 90.0

var rotacion: ComponenteRotacionCamara
var activado: bool = false


func _ready() -> void:
	rotacion = get_tree().get_first_node_in_group("rotacion_camara")
	animatronico.ataque_terminado.connect(jumpscare_terminado.emit)


func activar() -> void:
	if activado:
		return
	var turnos: ComponenteTurnosAtaque = get_tree().get_first_node_in_group("turnos_ataque") as ComponenteTurnosAtaque
	if turnos != null:
		if turnos.bloqueado or turnos.reloj.terminada:
			return
		turnos.detener()
	activado = true
	for computadora in get_tree().get_nodes_in_group("computadoras"):
		if computadora.escritorio.visible:
			computadora.cerrar()
	rotacion.set_process(false)
	rotacion.pivote.rotation_degrees.y = angulo_mirada
	rotacion.camara.rotation_degrees.x = 0.0
	animatronico.global_transform = punto.global_transform
	animatronico.visible = true
	animatronico.atacar()
	sonido.play()
