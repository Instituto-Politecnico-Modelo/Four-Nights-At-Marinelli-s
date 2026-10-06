extends Node

const RUTA: String = "user://guardado.json"
const ESCENA_NOCHE: String = "res://escenas/pasillo_orientacion.tscn"

var datos: Dictionary = {}
var continuar_partida: bool = false


func _ready() -> void:
	cargar()


func hay_partida() -> bool:
	return FileAccess.file_exists(RUTA)


func cargar() -> void:
	datos = {}
	if not hay_partida():
		return
	var archivo := FileAccess.open(RUTA, FileAccess.READ)
	if archivo == null:
		return
	var contenido: Variant = JSON.parse_string(archivo.get_as_text())
	archivo.close()
	if contenido is Dictionary:
		datos = contenido


func guardar() -> void:
	var archivo := FileAccess.open(RUTA, FileAccess.WRITE)
	if archivo == null:
		push_error("No se pudo escribir el archivo de guardado")
		return
	archivo.store_string(JSON.stringify(datos, "\t"))
	archivo.close()


func borrar() -> void:
	datos = {}
	continuar_partida = false
	if hay_partida():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(RUTA))


func nueva_partida() -> void:
	borrar()
	datos = {
		"escena": ESCENA_NOCHE,
		"noche": 1,
		"hora": 0,
	}
	guardar()


func cargar_partida() -> void:
	cargar()
	if datos.is_empty():
		nueva_partida()
		return
	continuar_partida = true


func escena_guardada() -> String:
	return str(datos.get("escena", ESCENA_NOCHE))


func noche_guardada() -> int:
	return int(datos.get("noche", 1))


func hora_guardada() -> int:
	return int(datos.get("hora", 0))


func guardar_avance(noche: int, hora: int) -> void:
	datos = {
		"escena": escena_guardada(),
		"noche": noche,
		"hora": hora,
	}
	guardar()
