import socket


class CheckingAnswers:
    def __init__(self, host):
        self.host = host
        self.port = 443

    def network_check(self):
        try:
            service_availability = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            service_availability.connect((self.host, self.port))
            return True
        except socket.error:
            return False
