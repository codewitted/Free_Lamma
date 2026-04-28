# ROS 2 LIMO Setup

Use ROS 2 Humble or Jazzy with Nav2 and LIMO robot packages. The current dispatcher is intentionally import-safe: without ROS 2 it logs mocked dispatch actions. For real robots, map each `navigate` plan action into a Nav2 `NavigateToPose` goal and connect pickup/drop to the available payload mechanism.

