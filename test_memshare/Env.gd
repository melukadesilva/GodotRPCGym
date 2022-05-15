extends Node2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var mem
var sem_act
var sem_obs

var action_tensor
var observation_tensor
var reward_tensor
var done_tensor

var action
var observation
var reward
var done

var timeout

var deltat = 0.01

# Called when the node enters the scene tree for the first time.
func _ready():
	mem = cSharedMemory.new()
	mem.init("env")
	sem_act = cSharedMemorySemaphore.new()
	sem_act.init("act_semaphore")
	sem_obs = cSharedMemorySemaphore.new()
	sem_obs.init("obs_semaphore")
	
	action_tensor = mem.findIntTensor("action");
	observation_tensor = mem.findFloatTensor("observation")
	reward_tensor = mem.findFloatTensor("reward")
	done_tensor = mem.findIntTensor("done")
	
	# give an initial observation
	print("timed out")
	observation = PoolRealArray([42, 32, 22])
	observation_tensor.write(observation)
	reward_tensor.write([reward])
	done_tensor.write([done])
	sem_obs.post()
	
	timeout = true
	
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if timeout:
		sem_act.wait()
		action = action_tensor.read()
		print("action received")
		print(action)
		
		# start/restart the timer
		$Timer.start(deltat)
		timeout = false
	else:
		print("Waiting for timeout")
#	pass


func _on_Timer_timeout():
	print("timed out")
	observation = PoolRealArray([42, 32, 22])
	observation_tensor.write(observation)
	reward = PoolRealArray([0.32])
	reward_tensor.write(reward)
	done = PoolIntArray([1])
	done_tensor.write(done)
	sem_obs.post()
	
	timeout = true
