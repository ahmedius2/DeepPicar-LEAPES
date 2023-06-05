from pololu_drv8835_rpi import motors, MAX_SPEED

# init
def init(default_speed=50):
    motors.setSpeeds(0, 0)
    set_speed(default_speed)

# throttle
cur_speed = MAX_SPEED
move_state = 0

def get_max_speed():
    return MAX_SPEED

def set_speed(speed):
    global cur_speed
    global move_state
    speed = int(MAX_SPEED * speed / 100)
    cur_speed = min(MAX_SPEED, speed)
    if move_state == -1:
        rew()
    elif move_state == 1:
        ffw()

def get_speed():
    return int(cur_speed * 100 / MAX_SPEED)

def stop():
    global move_state
    motors.motor2.setSpeed(0)
    move_state=0
        
def ffw():
    global move_state
    motors.motor2.setSpeed(cur_speed)
    move_state=1

def rew():
    global move_state
    motors.motor2.setSpeed(-cur_speed)
    move_state=-1

# steering
def center():
    motors.motor1.setSpeed(0)

def left(speed=-1):
    motors.motor1.setSpeed(int(speed*MAX_SPEED))

def right(speed=1):
    motors.motor1.setSpeed(int(speed*MAX_SPEED))

# exit    
def turn_off():
    stop()
    center()
