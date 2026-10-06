class_name ComponenteCarreraPuerta
extends Node

signal jumpscare_solicitado

@export var sonido_carrera: AudioStreamPlayer3D
@export var espera_inicial: float = 40.0
@export var reduccion_espera: float = 4.0
@export var espera_minima: float = 10.0
@export var carrera_inicial: float = 6.0
@export var reduccion_carrera: float = 0.4
@export var carrera_minima: float = 2.5

var puerta: ComponenteBisagra
var corriendo: bool = false
var activo: bool = true
var visitas: int = 0
var tiempo: float = 0.0


func _ready() -> void:
	puerta = get_tree().get_first_node_in_group("puerta_orientacion")
	tiempo = espera_inicial


func _process(delta: float) -> void:
	if not activo:
		return

	tiempo -= delta
	if tiempo > 0.0:
		return

	if corriendo:
		terminar_carrera()
	else:
		empezar_carrera()


func empezar_carrera() -> void:
	corriendo = true
	tiempo = maxf(carrera_inicial - reduccion_carrera * visitas, carrera_minima)
	sonido_carrera.play()


func terminar_carrera() -> void:
	corriendo = false
	sonido_carrera.stop()
	visitas += 1
	tiempo = maxf(espera_inicial - reduccion_espera * visitas, espera_minima)
	if not puerta.cerrada:
		activo = false
		jumpscare_solicitado.emit()
