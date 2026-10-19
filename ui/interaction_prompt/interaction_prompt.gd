extends CanvasLayer
class_name InteractionPrompt

@onready var etiqueta: Label = $Etiqueta


func _ready() -> void:
	etiqueta.visible = false
	SignalBus.interactuable_enfocado.connect(_on_enfocado)
	SignalBus.interactuable_desenfocado.connect(_on_desenfocado)
	SignalBus.interactuado.connect(_on_interactuado)


func _on_enfocado(interactuable: Node) -> void:
	etiqueta.text = "[E] %s" % interactuable.texto_interaccion
	etiqueta.visible = true


func _on_desenfocado(_interactuable: Node) -> void:
	etiqueta.visible = false


func _on_interactuado(interactuable: Node) -> void:
	print("Interactuado: ", interactuable.texto_interaccion)
