import serial.tools.list_ports
# 현재 pc에 연결되어 있는 포트의 리스트를 가져오는 구문

from devices import send_serial_command,send_camera_command
# device 폴더에 카메라,로봇.py에서 있는 함수를 가져오는 구문


ports = serial.tools.list_ports.comports()
# ports 변수를 선언하여 현제 연결된 COM들을 담아놓는다.

if not ports:
  print("연결된 포트가 없음")
  # ports 즉 현재 하드웨어상 연결되어 있는 포트가 없으면 출력 if문
else:
  for port in ports:
    print(port.device, "-", port.description)
    # 연결된 포트가 있으면 ports 수 만큼 loop하여 print로 device명과 상세내용 출력

robot_result = send_serial_command(port="COM99", command="MOVE P1")
print("로봇 결과: ", robot_result)

camera_result = send_camera_command(port="COM99", command="CAPTURE")
print("카메라 결과: ", camera_result)
#위와 같음