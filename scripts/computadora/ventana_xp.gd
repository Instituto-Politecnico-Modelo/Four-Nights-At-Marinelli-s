class_name VentanaXP
extends Panel

@export var titulo: String = "Ventana"
@export var programa: PackedScene
@export var etiqueta_titulo: Label
@export var boton_cerrar: Button
@export var contenido: Control


func _ready() -> void:
	etiqueta_titulo.text = titulo
	boton_cerrar.pressed.connect(hide)
	if programa != null:
		contenido.add_child(programa.instantiate())
