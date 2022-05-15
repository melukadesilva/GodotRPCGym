extends Area2D

signal hit

# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var screen_size

var velocity 
var direction

var frame_count = 0
var train = false

func reset():
	position = Vector2(rand_range(0, screen_size.x), rand_range(0, screen_size.y))
	#print(position)
	if train:
		velocity = Vector2(rand_range(150.0, 250.0), rand_range(150.0, 250.0))
	else:
		velocity = Vector2.ZERO
		
	show()
	
# Called when the node enters the scene tree for the first time.
func _ready():
	screen_size = get_viewport_rect().size
	$CollisionShape2D.disabled = false
	$AnimatedSprite.playing = true
	
	direction = rand_range(-PI / 4, PI / 4)
	reset()
	# randomize the direction
	#direction += rand_range(-PI / 4, PI / 4)
	#rotation = direction


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
#func update_player(delta):
	#frame_count += $AnimatedSprite.frames.get_frame_count("walk")
	#if frame_count % 6 == 0:
		#print(delta)
	#	direction += rand_range(-PI / 4, PI / 4)
	
	if train:
		rotation = direction
		position += velocity.rotated(direction) * delta
	else:
		rotation = direction
		position += velocity * delta# .rotated(direction) * delta
	
	# print("player", position)
	position.x = clamp(position.x, 0, screen_size.x)
	position.y = clamp(position.y, 0, screen_size.y)

func _on_Player_area_entered(area):
	print("Hit")
	hide()
	emit_signal("hit")
