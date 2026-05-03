# Example 1: Warehouse Coordination
# Subtask examination from action perspective:
# SubTask 1: Robot 1 deliver kit to station 3.
# SubTask 2: Robot 2 charge at station 1.

# coordination Actions:
# Robot 1 needs to reserve aisle_1 if Robot 2 is using it.
# reserve-aisle(?r, ?aisle_1)

# Assigned Robots: Robot 1, Robot 2
# Objects Involved: Kit, Station 1, Station 3, Aisle 1

# Domain file content:
(define (domain warehouse)
  (:requirements :strips :typing :negative-preconditions) 
  (:types robot loc item resource)
  (:predicates
    (at ?r - robot ?l - loc)
    (connected ?l1 - loc ?l2 - loc)
    (free ?res - resource)
    (reserved ?res - resource ?r - robot)
    (carrying ?r - robot ?i - item)
    (at-item ?i - item ?l - loc)
    (charger ?l - loc)
  )
  
  (:action navigate
    :parameters (?r - robot ?from - loc ?to - loc)
    :precondition (and (at ?r ?from) (connected ?from ?to))
    :effect (and (at ?r ?to) (not (at ?r ?from)))
  )

  (:action reserve-aisle
    :parameters (?r - robot ?res - resource)
    :precondition (free ?res)
    :effect (and (reserved ?res ?r) (not (free ?res)))
  )

  (:action release-aisle
    :parameters (?r - robot ?res - resource)
    :precondition (reserved ?res ?r)
    :effect (and (free ?res) (not (reserved ?res ?r)))
  )

  (:action pickup
    :parameters (?r - robot ?i - item ?l - loc)
    :precondition (and (at ?r ?l) (at-item ?i ?l))
    :effect (and (carrying ?r ?i) (not (at-item ?i ?l)))
  )

  (:action drop
    :parameters (?r - robot ?i - item ?l - loc)
    :precondition (and (at ?r ?l) (carrying ?r ?i))
    :effect (and (at-item ?i ?l) (not (carrying ?r ?i)))
  )

  (:action charge
    :parameters (?r - robot ?l - loc)
    :precondition (and (at ?r ?l) (charger ?l))
    :effect (and (not (inaction ?r))) ; Placeholder for charged state
  )
)

# Task Description: generate the problem file for Robot 1 delivering kit to station 3.
# Step 1: Identify Objects and Initial State
# Robots: robot1, robot2
# loc: kit_loc, station1, station3
# resource: aisle1
# kit: kit1

# Initial States:
# (at robot1 kit_loc)
# (at robot2 station3)
# (at-item kit1 kit_loc)
# (connected kit_loc station3)
# (free aisle1)
# (charger station1)

# Goals:
# (at-item kit1 station3)

# pddl
(define (problem warehouse_delivery_problem)
  (:domain warehouse)
  (:objects
    robot1 robot2 - robot
    kit_loc station1 station3 - loc
    kit1 - item
    aisle1 - resource
  )
  (:init
    (at robot1 kit_loc)
    (at robot2 station3)
    (at-item kit1 kit_loc)
    (connected kit_loc station3)
    (free aisle1)
    (charger station1)
  )
  (:goal
    (and
      (at-item kit1 station3)
    )
  )
)
# Problem file generation is done
