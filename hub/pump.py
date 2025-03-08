import RPi.GPIO as GPIO
import time

# Pin configuration
motorFI = 17  # Forward Input pin
motorBI = 27  # Backward Input pin

# Setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(motorFI, GPIO.OUT)
GPIO.setup(motorBI, GPIO.OUT)

# Give time for initialization
time.sleep(5)

i = 0

try:
    while True:
        i += 1
        print(f"loop! {i}")

        # Turn off LEDs initially
        GPIO.output(motorBI, GPIO.LOW)
        GPIO.output(motorFI, GPIO.LOW)
        print("initialized to LOW")

        time.sleep(1)

        # Simulate motor running forward
        GPIO.output(motorBI, GPIO.HIGH)
        GPIO.output(motorFI, GPIO.LOW)
        print("should be ON")

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()  # Cleanup GPIO settings
