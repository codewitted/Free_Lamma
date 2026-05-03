# Task Description: Robot 1 deliver kit to station 3, while Robot 2 charges at station 1.

# GENERAL TASK DECOMPOSITION 
# Decompose and parallelize subtasks where ever possible
# Independent subtasks:
# SubTask 1: Robot 1 deliver kit to station 3. (Skills Required: reserve-aisle, navigate, pickup, drop, release-aisle)
# SubTask 2: Robot 2 charge at station 1. (Skills Required: navigate, charge)
# We can parallelize SubTask 1 and SubTask 2.

# action description from domain for tasks required:

# Subtask 1: Robot 1 deliver kit to station 3
# Actions:
# reserve-aisle: Robot 1 reserves aisle_A if needed for navigation.
# navigate: Robot 1 moves to kit_location.
# pickup: Robot 1 picks up the kit.
# navigate: Robot 1 moves to station 3.
# drop: Robot 1 drops the kit at station 3.
# release-aisle: Robot 1 releases aisle_A.

# Subtask 2: Robot 2 charge at station 1
# Actions:
# navigate: Robot 2 moves to station 1 (charger location).
# charge: Robot 2 charges at station 1.

# coordination logic:
# If both robots need the same aisle, the solver will sequence the reserve/release actions.
