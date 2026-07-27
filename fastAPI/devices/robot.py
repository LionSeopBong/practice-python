# devices/robot.py
import serial

def send_serial_command(port: str, command: str, baudrate: int = 9600) -> str | None:
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=2, write_timeout=2) as ser:
            ser.write(command.encode("utf-8") + b"\n")
            response = ser.readline().decode("utf-8").strip()
            return response
    except serial.SerialException as e:
        print(f"시리얼 통신 실패: {e}")
        return None