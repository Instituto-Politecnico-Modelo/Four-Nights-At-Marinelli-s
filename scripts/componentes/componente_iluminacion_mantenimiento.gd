class_name ComponenteIluminacionMantenimiento
extends Node

@export var sistema: ComponenteSistemaMantenimiento
@export var luces: Array[Light3D] = []
@export var tubos: Array[MeshInstance3D] = []
@export var parpadeos: Array[ComponenteParpadeoLuz] = []

var visibilidad: Array[bool] = []
var materiales: Array[StandardMaterial3D] = []
var emisiones: Array[float] = []
var modos: Array[int] = []


func _ready() -> void:
	for luz in luces:
		visibilidad.append(luz.visible)
	for tubo in tubos:
		var original: StandardMaterial3D = tubo.get_surface_override_material(0) as StandardMaterial3D
		var material: StandardMaterial3D = original.duplicate() as StandardMaterial3D
		tubo.set_surface_override_material(0, material)
		materiales.append(material)
		emisiones.append(material.emission_energy_multiplier)
		for parpadeo in parpadeos:
			if parpadeo.material_tubo == original:
				parpadeo.material_tubo = material
	for parpadeo in parpadeos:
		modos.append(parpadeo.process_mode)
	sistema.estado_cambiado.connect(_actualizar)
	_actualizar()


func _actualizar() -> void:
	var encendidas: bool = sistema.operativo()
	for i in parpadeos.size():
		parpadeos[i].process_mode = modos[i] if encendidas else Node.PROCESS_MODE_DISABLED
	for i in luces.size():
		luces[i].visible = visibilidad[i] and encendidas
	for i in materiales.size():
		materiales[i].emission_energy_multiplier = emisiones[i] if encendidas else 0.0
