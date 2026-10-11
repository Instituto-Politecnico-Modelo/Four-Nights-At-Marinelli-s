class_name ZonaMonitor
extends Area3D

signal clickeado

@export var alcance: float = 3.0


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT):
		return
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		return
	var camara: Camera3D = get_viewport().get_camera_3d()
	if camara == null:
		return
	var origen: Vector3 = camara.global_position
	var destino: Vector3 = origen - camara.global_transform.basis.z * alcance
	var consulta := PhysicsRayQueryParameters3D.create(origen, destino)
	consulta.collide_with_areas = true
	consulta.collide_with_bodies = false
	var resultado: Dictionary = get_world_3d().direct_space_state.intersect_ray(consulta)
	if resultado and resultado.collider == self:
		clickeado.emit()
