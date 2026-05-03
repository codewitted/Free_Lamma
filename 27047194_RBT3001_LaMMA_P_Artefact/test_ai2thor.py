import ai2thor.controller
import time

def test_controller():
    print("Testing AI2-THOR controller initialization...")
    try:
        # Starting with a small timeout or just seeing if it gets past the first line
        controller = ai2thor.controller.Controller(scene="FloorPlan6")
        print("Successfully initialized controller!")
        objs = controller.last_event.metadata["objects"]
        print(f"Found {len(objs)} objects.")
        controller.stop()
    except Exception as e:
        print(f"Controller initialization failed: {str(e)}")

if __name__ == "__main__":
    test_controller()
