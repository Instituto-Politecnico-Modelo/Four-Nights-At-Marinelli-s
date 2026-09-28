extends Area2D
class_name InteractableComponent
## InteractableComponent
## Componente base para cualquier objeto con el que Charlie pueda interactuar.
## No define su propia forma de colision: cada escena duenia (computadora,
## laptop, escondite, etc.) le agrega su propio CollisionShape2D con el
## alcance que corresponda.

@export var texto_interaccion: String = "Interactuar"

signal interactuado()
