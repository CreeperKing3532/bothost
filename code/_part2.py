import json
import requests
import concurrent.futures
import os

def send_webhook_message(session, webhook_url, message):
    payload = {"content": message}
    try:
        response = session.post(webhook_url, json=payload)
        if response.status_code != 204:
            return f"Failed: {webhook_url} - {response.status_code}"
    except Exception as e:
        return f"Error: {webhook_url} - {e}"
    return None

def load_hooks(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            return data  # your file is just a list
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def process_webhooks(hooks, message):
    with requests.Session() as session:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(hooks)) as executor:
            futures = [executor.submit(send_webhook_message, session, hook, message) for hook in hooks]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    print(result)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hooks_file = os.path.join(current_dir, "webhooks.json")
    hooks = load_hooks(hooks_file)

    if not hooks:
        print("No webhooks found.")
        return

    message = "@everyone"

    while True:
        process_webhooks(hooks, message)  # no delay, send ASAP nonstop

if __name__ == "__main__":
    main()
