class_name ProgramaCamaras
extends Control

@export var camara: Camera3D
@export var lista: VBoxContainer
@export var nombre: Label
@export var vista: Control
@export var aviso: Label

var puntos: Array[Node] = []
var interferencia: ComponenteInterferenciaCamaras
var sistema_camaras: ComponenteSistemaMantenimiento
var sistema_servidor: ComponenteSistemaMantenimiento
var reinicio: ComponenteReinicioMantenimiento


func _ready() -> void:
	interferencia = get_tree().get_first_node_in_group("interferencia_camaras")
	sistema_camaras = get_tree().get_first_node_in_group("sistema_camaras") as ComponenteSistemaMantenimiento
	sistema_servidor = get_tree().get_first_node_in_group("sistema_servidor") as ComponenteSistemaMantenimiento
	reinicio = get_tree().get_first_node_in_group("reinicio_mantenimiento") as ComponenteReinicioMantenimiento
	puntos = get_tree().get_nodes_in_group("camaras_seguridad")
	for i in puntos.size():
		var boton: Button = Button.new()
		boton.text = puntos[i].name
		boton.pressed.connect(seleccionar.bind(i))
		lista.add_child(boton)

	if puntos.size() > 0:
		seleccionar(0, false)


func _process(_delta: float) -> void:
	var apagada: bool = interferencia != null and interferencia.apagada()
	if sistema_camaras != null and not sistema_camaras.operativo():
		apagada = true
		aviso.text = "ERROR DE CÁMARAS\nReiniciar desde Mantenimiento"
	elif reinicio != null and reinicio.activo():
		apagada = true
		aviso.text = "MANTENIMIENTO EN CURSO"
	else:
		aviso.text = "SIN SEÑAL"
	vista.visible = not apagada
	aviso.visible = apagada
	var servidor_caido: bool = sistema_servidor != null and not sistema_servidor.operativo()
	for boton in lista.get_children():
		boton.disabled = servidor_caido or apagada
	nombre.text = "SERVIDOR SIN CONEXIÓN · cámara bloqueada" if servidor_caido else (camara.get_meta("nombre_camara", "CAM") as String)


func seleccionar(indice: int, con_sonido: bool = true) -> void:
	if con_sonido and ((sistema_servidor != null and not sistema_servidor.operativo()) or (sistema_camaras != null and not sistema_camaras.operativo()) or (reinicio != null and reinicio.activo())):
		return
	var punto: Node3D = puntos[indice]
	camara.global_transform = punto.global_transform
	camara.set_meta("nombre_camara", String(punto.name))
	nombre.text = punto.name
	if con_sonido:
		Sonidos.camara()
