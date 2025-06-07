""" misc helpers for running tasks """
import copy
import requests

class HyperHDRController:
    """ controller class for sending json requests to hyperhdr """
    def __init__(self, host='localhost', port=8090) -> None:
        self.url = f'http://{host}:{port}/json-rpc'
        self.session = requests.Session()
        self.tan = 1

    def _send(self, payload, retries=3) -> list:
        """ internal send payload method """
        responses = []
        for _ in range(retries):
            request_payload = copy.deepcopy(payload)
            request_payload['tan'] = self.tan
            self.tan += 1
            try:
                response = self.session.post(self.url, json=request_payload)
                response.raise_for_status()
                result = response.json()
                responses.append(result)
                if result.get("success"):
                    break
            except requests.RequestException as e:
                responses.append({"success": False, "error": str(e)})
        return responses

    def leds_off(self) -> list:
        """ turn leds off """
        return self._send({
            "command": "componentstate",
            "componentstate": {
                "component": "LEDDEVICE",
                "state": False
            }
        })

    def leds_on(self) -> list:
        """ turn leds on """
        return self._send({
            "command": "componentstate",
            "componentstate": {
                "component": "LEDDEVICE",
                "state": True
            }
        })
