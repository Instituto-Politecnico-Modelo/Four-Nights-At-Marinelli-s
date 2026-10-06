class_name ProgramaCamaras
extends Control

@export var camara: Camera3D
@export var lista: VBoxContainer
@export var nombre: Label
@export var vista: Control
@export var aviso: Label

var puntos: Array[Node] = []
var interferencia: ComponenteInterferenciaCamaras


func _ready() -> void:
	interferencia = get_tree().get_first_node_in_group("interferencia_camaras")
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
	vista.visible = not apagada
	aviso.visible = apagada


func seleccionar(indice: int, con_sonido: bool = true) -> void:
	var punto: Node3D = puntos[indice]
	camara.global_transform = punto.global_transform
	nombre.text = punto.name
	if con_sonido:
		Sonidos.camara()
