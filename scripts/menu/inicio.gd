extends Control

@export var video: VideoStreamPlayer
@export var musica: AudioStreamPlayer

var cambiando_escena: bool = false


func _ready() -> void:
	if video != null and not video.is_playing():
		video.play()
	if musica != null:
		if not musica.finished.is_connected(_repetir_musica):
			musica.finished.connect(_repetir_musica)
		if not musica.playing:
			musica.play()


func _repetir_musica() -> void:
	musica.play()


func _on_boton_nuevo_juego() -> void:
	Sonidos.boton_inicio()
	Guardado.nueva_partida()
	cambiar_escena(Guardado.ESCENA_NOCHE)


func _on_boton_continuar() -> void:
	Sonidos.boton_inicio()
	Guardado.cargar_partida()
	cambiar_escena(Guardado.escena_guardada())


func cambiar_escena(ruta: String) -> void:
	if cambiando_escena:
		return
	cambiando_escena = true
	if video != null:
		video.stop()
	if musica != null:
		musica.stop()
	var error := get_tree().change_scene_to_file(ruta)
	if error != OK:
		cambiando_escena = false
		push_error("No se pudo cargar la escena: %s" % ruta)
