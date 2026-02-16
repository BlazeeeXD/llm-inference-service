import requests
import json

url = "http://localhost:8000/v1/chat/completions"

payload = {
    "model": "gpt-3.5-turbo", 
    "messages": [
        {"role": "user", "content": "List 3 colors."}
    ],
    "stream": True,
    "temperature": 0.7
}

print("Sending request to API...")
with requests.post(url, json=payload, stream=True) as response:
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:] 
                    if json_str == "[DONE]":
                        print("\n[Stream Finished]")
                        break
                    try:
                        data = json.loads(json_str)
                        delta = data['choices'][0]['delta']
                        if 'content' in delta:
                            print(delta['content'], end="", flush=True)
                    except:
                        pass
    else:
        print(f"Error: {response.status_code} - {response.text}")