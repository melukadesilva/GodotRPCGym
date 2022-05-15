extends Node2D

var agent_action = [0.0]
var env_action = [0, 0]

var sem_action
var sem_observation
var sem_physics

var mem
var env_action_tensor
var agent_action_tensor
var observation_tensor
var reward_tensor
var done_tensor


# onready var policy_data = load("res://ddpg_policy.tres")
onready var policy_data = load("res://ddpg_actor.tres")
var policy
var policy_action

var reset = false
var timeout = true
var deltat = 0.05
var time_elapsed = 0.0
var prev_time = 0.0
var sem_delta = 0.0
var target_delta = 0.025

var max_num_steps = 500
var num_steps = 0

var count = 0

var train = true

func _ready():
	var v = $Anchor/PinJoint2D/RigidBody2D.transform.get_origin()
	var AnchorT = $Anchor.transform
	var JointT = $Anchor/PinJoint2D.transform
	$Anchor/PinJoint2D/RigidBody2D.init_anchor = AnchorT.xform(JointT.get_origin())
	$Anchor/PinJoint2D/RigidBody2D.init_origin = AnchorT.xform(JointT.xform(v))
	$Anchor/PinJoint2D/RigidBody2D.init_rotation = 0.0
	$Anchor/PinJoint2D/RigidBody2D.init_angular_velocity = 1.0
	$Anchor/PinJoint2D/RigidBody2D.reset = true
	
	mem = cSharedMemory.new()
	mem.init("env")
	sem_physics = Semaphore.new()
	sem_physics.post()
	print(mem.exists())
	if train:
		print("In the if")
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
		
		var observation = $Anchor/PinJoint2D/RigidBody2D.get_observation()
		var reward = [$Anchor/PinJoint2D/RigidBody2D.get_reward()]
		observation_tensor.write(observation)
		reward_tensor.write(reward)
		done_tensor.write([is_done()])
		sem_observation.post()
	else:
		print("Running as a game")
		policy = cTorchModel.new()
		policy.set_data(policy_data)
	
	set_physics_process(true)

func is_done():
	if num_steps>=max_num_steps:
		num_steps = 0
		return 1
	else:
		return 0
	
func _process(delta):
	if mem.exists():
		var cur_time = OS.get_ticks_usec()
		var t = cur_time - prev_time - sem_delta
		if t < 0:
			print(t)
		var fps_est = 1000000.0/(cur_time - prev_time - sem_delta)
		Engine.set_iterations_per_second(fps_est)
		Engine.set_time_scale(Engine.get_iterations_per_second()*target_delta)
		sem_delta = 0.0
		prev_time = cur_time
	
func _physics_process(delta):
	if timeout:
		sem_physics.wait()
		if mem.exists():
			var time_start = OS.get_ticks_usec()
			sem_action.wait()
			var time_end = OS.get_ticks_usec()
			sem_delta = time_end - time_start
			agent_action = agent_action_tensor.read()
			# print(agent_action)
			env_action = env_action_tensor.read()
		else:
			agent_action[0] = 0.0
			env_action[0] = 0
			env_action[1] = 0
			if Input.is_action_pressed("ui_right"):
				agent_action[0] = 1.0
			if Input.is_action_pressed("ui_left"):
				agent_action[0] = -1.0
			if Input.is_key_pressed(KEY_ENTER):
				env_action[0] = 1
			if Input.is_key_pressed(KEY_ESCAPE):
				env_action[1] = 1
			if policy_action != null:
				agent_action = policy_action
			agent_action[0]*=8.0
		
		$ActionLabel.text = "Action: "+str(agent_action[0])
		#print(env_action)
		if env_action[0] == 1:
		#if is_done() == 1:
			#print("Done")
			#get_tree().paused = true
			$Anchor/PinJoint2D/RigidBody2D.reset = true
			time_elapsed = 0.0
			#get_tree().paused = false
		
		if env_action[1] == 1:
			get_tree().quit()
		$Anchor/PinJoint2D/RigidBody2D.torque = -agent_action[0]/1.0
		#if agent_action[0] == 0:
		#	$Anchor/PinJoint2D/RigidBody2D.torque = -3
		#elif agent_action[0] == 1:
		#	$Anchor/PinJoint2D/RigidBody2D.torque = 3
		#else:
		#	print("Invalid action")
		
		$Timer.start(deltat)
		timeout = false
		sem_physics.post()
		

func _on_Timer_timeout():
	# print("timeout")
	sem_physics.wait()
	var observation = $Anchor/PinJoint2D/RigidBody2D.get_observation()
	var reward = [$Anchor/PinJoint2D/RigidBody2D.get_reward()]
	$ObservationLabel.text = "Observation: "+str(observation)
	$RewardLabel.text = "Reward: "+str(reward)
	$TimeLabel.text = "Time:"+str(time_elapsed)
	if mem.exists():
		observation_tensor.write(observation)
		reward_tensor.write(reward)
		var done = is_done()
		#if done == 1:
		#	print(done)
		done_tensor.write([done])
		sem_observation.post()
	else:
		policy_action = policy.run(observation)
	
	time_elapsed += deltat
	num_steps += 1
	timeout = true
	sem_physics.post()
