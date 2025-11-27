# import RPi.GPIO as GPIO
import time

_MOTOR_FI = 17  # Forward Input pin
_MOTOR_BI = 27  # Backward Input pin

_PUMP_DURATION_SECONDS = 5

class PumpController():
    def __init__(self):
        print("PumpController initialized")
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(_MOTOR_FI, GPIO.OUT)
        # GPIO.setup(_MOTOR_BI, GPIO.OUT)

        # GPIO.output(_MOTOR_BI, GPIO.LOW)
        # GPIO.output(_MOTOR_FI, GPIO.LOW)

    def on(self):
        """Activate the pump. Currently a stub implementation."""
        # GPIO.output(_MOTOR_BI, GPIO.HIGH)
        # GPIO.output(_MOTOR_FI, GPIO.LOW)
        # time.sleep(_PUMP_DURATION_SECONDS)
        # GPIO.output(_MOTOR_BI, GPIO.LOW)
        # GPIO.output(_MOTOR_FI, GPIO.LOW)
        pass