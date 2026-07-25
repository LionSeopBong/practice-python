from devices import Robot,load_camera_config


config = load_camera_config("camera_config.json")
print(config)

ur5 = Robot.from_config_file("robot_config.json")
ur5.move("P1",1.5)
ur5.move("P2",3.0)
