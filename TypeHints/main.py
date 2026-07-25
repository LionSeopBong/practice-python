from devices import get_camera_status, Robot

status = get_camera_status()
print("결과:",status)

ur5 = Robot("UR5", max_speed=2.0)
ur5.move("P1",1.5)
ur5.move("P2",3.0)
