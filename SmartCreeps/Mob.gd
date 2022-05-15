extends Area2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var screen_size
var direction
var velocity

var frame_count = 0

func reset():
	direction = 0.0
	velocity = Vector2.ZERO
	position = Vector2(rand_range(0, screen_size.x), rand_range(0, screen_size.y))
	
# Called when the node enters the scene tree for the first time.
func _ready():
	screen_size = get_viewport_rect().size
	# set the annimations to true
	$AnimatedSprite.playing = true
	# get the number of animations; returns a list of annimations
	var mob_type = $AnimatedSprite.frames.get_animation_names()
	# Set a random animation
	$AnimatedSprite.animation = "flying" #mob_type[randi() % mob_type.size()]
	reset()
	#position = mob_spawn_location.position# + Vector2(rand_range(0, screen_size.x), rand_range(0, screen_size.y))


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	rotation = direction
	position += velocity * delta
	# print("mob: ", position)
	# linear_velocity = velocity.rotated(direction)
	#print(velocity)
	position.x = clamp(position.x, 0, screen_size.x)
	position.y = clamp(position.y, 0, screen_size.y)
