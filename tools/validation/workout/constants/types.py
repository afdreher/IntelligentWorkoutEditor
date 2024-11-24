WORKOUT = 'workout'

SPEED = 'speed'
HEART_RATE = 'heart_rate'
HEART_RATE_ZONE = 'heart_rate_zone'
CADENCE = 'cadence'
POWER = 'power'
LAP_TIME = 'lap_time'

STEP_GOALS = {
    'speed': SPEED,
    'pace': SPEED,
    'heart_rate': HEART_RATE,
    'hr': HEART_RATE,
    'heart_rate_zone': HEART_RATE_ZONE,
    'hr_zone': HEART_RATE_ZONE,
    'zone': HEART_RATE_ZONE,
    'cadence': CADENCE,
    'power': POWER,
    'lap_time': LAP_TIME,
    'lap': LAP_TIME,
    'time': LAP_TIME
}

VALID_STEP_GOALS = [
    SPEED, HEART_RATE, HEART_RATE_ZONE, CADENCE, POWER, LAP_TIME
]



# These constants allow some flexibility in case the LLM doesn't *exactly* follow the instructions

REPETITION = 'repetition'

RUN = 'run'
RECOVER = 'recover'
REST = 'rest'
WARM_UP = 'warm-up'
COOL_DOWN = 'cool-down'

REPETITION_STEPS = [
    REPETITION,
    'repeat',
    'loop'
]

WORKOUT_STEPS = {
    'run': RUN,
    'work': RUN,
    'recover': RECOVER,
    'recovery': RECOVER,
    'rest': REST,
    'break': REST,
    'warm-up': WARM_UP,
    'warmup': WARM_UP,
    'wu': WARM_UP,
    'cool-down': COOL_DOWN,
    'cooldown': COOL_DOWN,
    'cd': COOL_DOWN,
}

VALID_STEPS = [
    REPETITION, RUN, RECOVER, REST, WARM_UP, COOL_DOWN
]
