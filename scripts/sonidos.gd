extends Node

const CANTIDAD_REPRODUCTORES: int = 8

const PERSIANA: AudioStream = preload("res://EfectosDeSonidos/persiana.mp3")
const PUERTA: AudioStream = preload("res://EfectosDeSonidos/door.mp3")
const CAMBIO_CAMARA: AudioStream = preload("res://EfectosDeSonidos/CambiodeCamara.mp3")
const SEIS_AM: AudioStream = preload("res://EfectosDeSonidos/6am.mp3")
const JUMPSCARE_PRUSBONNIE: AudioStream = preload("res://EfectosDeSonidos/JumpscarePrusBonnie.mp3")
const JUMPSCARE_MARIFREDDY: AudioStream = preload("res://EfectosDeSonidos/JumpscareMaryfreddy.mp3")
const SELECCION_BOTON: AudioStream = preload("res://EfectosDeSonidos/Seleccionbotoninicio.mp3")

var reproductores: Array[AudioStreamPlayer] = []
var siguiente: int = 0


func _ready() -> void:
	for i in CANTIDAD_REPRODUCTORES:
		var reproductor := AudioStreamPlayer.new()
		add_child(reproductor)
		reproductores.append(reproductor)


func reproducir(stream: AudioStream, volumen_db: float = 0.0) -> void:
	if stream == null:
		return
	var reproductor := _libre()
	reproductor.stream = stream
	reproductor.volume_db = volumen_db
	reproductor.play()


func persiana() -> void:
	reproducir(PERSIANA)


func puerta() -> void:
	reproducir(PUERTA)


func camara() -> void:
	reproducir(CAMBIO_CAMARA)


func seis_am() -> void:
	reproducir(SEIS_AM)


func jumpscare_prusbonnie() -> void:
	reproducir(JUMPSCARE_PRUSBONNIE)


func jumpscare_marifreddy() -> void:
	reproducir(JUMPSCARE_MARIFREDDY)


func boton_inicio() -> void:
	reproducir(SELECCION_BOTON)


func _libre() -> AudioStreamPlayer:
	for reproductor in reproductores:
		if not reproductor.playing:
			return reproductor
	siguiente = (siguiente + 1) % reproductores.size()
	return reproductores[siguiente]
