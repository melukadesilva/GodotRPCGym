extends Node


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var mob
var mob_pos

var player
var player_pos
var player_animation
var frame_count = 0

var distant
var distant_reward = 0.0
var hit_reward = 0.0
var total_reward

var is_done = 0
var timeout = true
var deltat = 0.05

var pos_obs_x
var pos_obs_y
var velo_obs_x
var velo_obs_y

var m_pos_obs_x
var m_pos_obs_y
var m_velo_obs_x
var m_velo_obs_y
var p_pos_obs_x
var p_pos_obs_y
var p_velo_obs_x
var p_velo_obs_y
var observations

var mem
var sem_action
var sem_observation
var agent_action_tensor
var env_action_tensor
var reward_tensor
var observation_tensor
var done_tensor

var action
var env_action

var train = true
var time_elapsed = 0.0
var episode_length = 400
var timeout_count = 0

var policy
onready var policy_data = load('res://ppo_actor.tres') # load once entering the tree (var only created when the
var policy_action = [0.0, 0.0, 0.0]

func apply_action(action):
	mob.velocity = Vector2(action[0], action[1])
	mob.direction = action[2]

func get_distance_reward():
	player_pos = player.position
	mob_pos = mob.position
	
	distant = sqrt(pow((player_pos.x - mob_pos.x), 2) + pow((player_pos.y - mob_pos.y), 2))
	distant_reward += 1 / (distant+1e-6)
	# distant_reward = distant_reward - time_elapsed * 1e-2

func reset():
	print("Resetting")
	mob.reset()
	player.reset()
	
	hit_reward = 0.0
	distant_reward = 0.0
	is_done = 0
	timeout_count = 0

# Called when the node enters the scene tree for the first time.
func _ready():
	randomize()
	mob = $Mob
	player = $Player

	mem = cSharedMemory.new()
	mem.init("env")
	if train:
		player.train = true
		player_animation = player.get_node("AnimatedSprite")
		sem_action = cSharedMemorySemaphore.new()
		sem_observation = cSharedMemorySemaphore.new()

		sem_action.init("act_semaphore")
		sem_observation.init("obs_semaphore")
		
		#agent_action_tensor = mem.findIntTensor("action")
		agent_action_tensor = mem.findFloatTensor("action")
		env_action_tensor = mem.findIntTensor("env_action")
		reward_tensor = mem.findFloatTensor("reward")
		observation_tensor = mem.findFloatTensor("observation")
		done_tensor = mem.findIntTensor("done")
		print("Running as OpenAIGym environment")
	else:
		policy = cTorchModel.new()
		policy.set_data(policy_data)
		print("Model loaded")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if timeout:
		if train:
			frame_count += player_animation.frames.get_frame_count("walk")
			if frame_count % 6 == 0:
				#print(delta)
				player.direction += rand_range(-PI / 4, PI / 4)
				
			sem_action.wait()
			action = agent_action_tensor.read()
			env_action = env_action_tensor.read()
			# print(action)
			
			if env_action[0] == 1:
				reset()
				time_elapsed = 0.0
			if env_action[1] == 1:
				get_tree().quit()	
		else:
			if is_done == 1:
				reset()
			player.velocity = Vector2.ZERO
			if Input.is_action_pressed("move_right"):
				player.velocity.x += 400
			if Input.is_action_pressed("move_left"):
				player.velocity.x -= 400
			if Input.is_action_pressed("move_up"):
				player.velocity.y -= 400
			if Input.is_action_pressed("move_down"):
				player.velocity.y += 400
				
			action = policy_action
		
		#player.update_player(delta)
		get_distance_reward()
		print(action)
		apply_action(action)
		
		$Timer.start(deltat)
		timeout = false
		#print(timeout_count)
		# If episode length is over some value
		if fmod(timeout_count, episode_length) == 0 and timeout_count != 0:
			# print(timeout_count)
			hit_reward = -100
			is_done = 1

		timeout_count += 1
	
		
	
func game_over():
	hit_reward = 100.0
	is_done = 1
	# get_tree().paused = true

func _on_Timer_timeout():
	total_reward = hit_reward + distant_reward
	
	#pos_obs_x = abs(player_pos.x - mob_pos.x)
	#pos_obs_y = abs(player_pos.y - mob_pos.y)
	#velo_obs_x = abs(player.velocity.x - mob.velocity.x)
	#velo_obs_y = abs(player.velocity.y - mob.velocity.y)
	print(mob_pos)
	m_pos_obs_x = mob_pos.x
	m_pos_obs_y = mob_pos.y
	m_velo_obs_x = mob.velocity.x
	m_velo_obs_y = mob.velocity.y
	p_pos_obs_x = player_pos.x
	p_pos_obs_y = player_pos.y
	p_velo_obs_x = player.velocity.x
	p_velo_obs_y = player.velocity.y
	#observations = [pos_obs_x / 480.0, pos_obs_y / 720.0, velo_obs_x / 250.0, velo_obs_y / 250.0]
	observations = [m_pos_obs_x / 480.0, m_pos_obs_y / 720.0, 
					m_velo_obs_x / 250.0, m_velo_obs_y / 250.0,
					p_pos_obs_x / 480.0, p_pos_obs_y / 720.0, 
					p_velo_obs_x / 250.0, p_velo_obs_y / 250.0]
	
	# print(total_reward)
	# print(pos_obs_x)
	# print(pos_obs_y)
	if train:
		observation_tensor.write(observations)
		reward_tensor.write([total_reward])
		done_tensor.write([is_done])
		
		sem_observation.post()
	else:
		print("run model")
		policy_action = policy.run(observations)
		policy_action[0] = policy_action[0] * 250.0
		policy_action[1] = policy_action[1] * 250.0
		policy_action[2] = policy_action[2] * PI
		
		print(policy_action)
	
	time_elapsed += deltat
	timeout = true
	
	# print(time_elapsed)
	
	
	
	
