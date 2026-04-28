(define (domain open_lamma_r)
  (:requirements :strips :typing :negative-preconditions)
  (:types robot location item capability)
  (:predicates
    (robot ?r - robot)
    (location ?l - location)
    (object ?o - item)
    (at ?r - robot ?l - location)
    (connected ?from - location ?to - location)
    (carrying ?r - robot ?o - item)
    (object-at ?o - item ?l - location)
    (available ?r - robot)
    (has-capability ?r - robot ?c - capability)
    (battery-ok ?r - robot)
    (inspected ?l - location)
    (task-complete ?t - item)
  )

  (:action navigate
    :parameters (?r - robot ?from - location ?to - location)
    :precondition (and (robot ?r) (available ?r) (at ?r ?from) (connected ?from ?to) (battery-ok ?r) (has-capability ?r navigate))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup
    :parameters (?r - robot ?o - item ?l - location)
    :precondition (and (available ?r) (at ?r ?l) (object-at ?o ?l) (has-capability ?r pickup))
    :effect (and (carrying ?r ?o) (not (object-at ?o ?l)))
  )

  (:action drop
    :parameters (?r - robot ?o - item ?l - location)
    :precondition (and (available ?r) (at ?r ?l) (carrying ?r ?o) (has-capability ?r drop))
    :effect (and (object-at ?o ?l) (not (carrying ?r ?o)) (task-complete ?o))
  )

  (:action inspect
    :parameters (?r - robot ?l - location)
    :precondition (and (available ?r) (at ?r ?l) (has-capability ?r inspect))
    :effect (and (inspected ?l))
  )

  (:action meet
    :parameters (?r1 - robot ?r2 - robot ?l - location)
    :precondition (and (available ?r1) (available ?r2) (at ?r1 ?l) (at ?r2 ?l))
    :effect (and (available ?r1) (available ?r2))
  )

  (:action charge
    :parameters (?r - robot ?l - location)
    :precondition (and (available ?r) (at ?r ?l) (has-capability ?r charge))
    :effect (and (battery-ok ?r))
  )

  (:action wait
    :parameters (?r - robot ?l - location)
    :precondition (and (available ?r) (at ?r ?l))
    :effect (and (available ?r))
  )
)

