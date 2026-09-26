class_name ProgramaCamaras
extends Control

@export var camara: Camera3D
@export var lista: VBoxContainer
@export var nombre: Label

var puntos: Array[Node] = []


func _ready() -> void:
	puntos = get_tree().get_nodes_in_group("camaras_seguridad")
	for i in puntos.size():
		var boton: Button = Button.new()
		boton.text = puntos[i].name
		boton.pressed.connect(seleccionar.bind(i))
		lista.add_child(boton)

	if puntos.size() > 0:
		seleccionar(0)


func seleccionar(indice: int) -> void:
	var punto: Node3D = puntos[indice]
	camara.global_transform = punto.global_transform
	nombre.text = punto.name
