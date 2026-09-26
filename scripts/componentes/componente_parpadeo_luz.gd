class_name ComponenteParpadeoLuz
extends Node

@export var luz: Light3D
@export var material_tubo: StandardMaterial3D
@export var probabilidad_apagado: float = 0.2
@export var intervalo_minimo: float = 0.04
@export var intervalo_maximo: float = 0.8

var energia_luz: float = 0.0
var energia_tubo: float = 0.0
var tiempo: float = 0.0


func _ready() -> void:
	energia_luz = luz.light_energy
	energia_tubo = material_tubo.emission_energy_multiplier


func _process(delta: float) -> void:
	tiempo -= delta
	if tiempo > 0.0:
		return

	tiempo = randf_range(intervalo_minimo, intervalo_maximo)
	if randf() < probabilidad_apagado:
		luz.light_energy = energia_luz * 0.05
		material_tubo.emission_energy_multiplier = energia_tubo * 0.05
	else:
		luz.light_energy = energia_luz
		material_tubo.emission_energy_multiplier = energia_tubo
