"""PushStq messaging module."""

import requests

from config import ProjectConfig

config = ProjectConfig()


def pushstaq_push_message(message: str) -> None:
    """Post message to the PushStaq service.

    :param message: message to be post to PushStaq
    """
    url = config.pushstaq_api_url

    headers = {
        "Content-Type": "application/json",
        "x-api-key": config.pushstaq_api_key.get_secret_value(),
    }
    json_message = {"message": message}
    request = requests.post(url=url, headers=headers, json=json_message)
    print(request.status_code, request.json())


if __name__ == "__main__":
    pushstaq_push_message(message="hello from API!")
