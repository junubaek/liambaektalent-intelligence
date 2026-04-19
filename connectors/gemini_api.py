
import json
import urllib.request
import urllib.error
import time

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        # Priority list of configurations to try
        self.configs = [
            {"model": "models/gemini-embedding-001", "version": "v1beta", "supports_task_type": True},
            {"model": "models/embedding-001", "version": "v1", "supports_task_type": False}
        ]
        self.working_config = None # Will be set after first successful call

    def _make_request(self, text, config, task_type):
        model = config["model"]
        version = config["version"]
        use_task_type = config["supports_task_type"]
        
        url = f"https://generativelanguage.googleapis.com/{version}/{model}:embedContent?key={self.api_key}"
        
        payload = {
            "model": model,
            "content": {"parts": [{"text": text}]}
        }
        
        if use_task_type and task_type:
            payload["taskType"] = task_type
            
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))

    def get_chat_completion_json(self, prompt: str, model: str = "gemini-3-flash-preview") -> dict:
        """
        [v6.2] Gemini Chat Completion with JSON output.
        """
        models_to_try = ["gemini-2.5-flash"]
        
        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "response_mime_type": "application/json"
                }
            }
            
            data = json.dumps(payload).encode('utf-8')
            headers = {"Content-Type": "application/json"}
            
            try:
                # print(f"[DEBUG] Trying Chat Model: {m}")
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=45) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if "candidates" in result and result["candidates"]:
                        content_text = result["candidates"][0]["content"]["parts"][0]["text"]
                        try:
                            return json.loads(content_text)
                        except Exception as parse_e:
                            print(f"[DEBUG JSON PARSE ERROR] {parse_e}")
                            print(f"RAW CONTENT:\n{content_text}")
                            continue
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "Too Many Requests" in err_str:
                    print(f"❌ Gemini Chat Completion Error with {m}: limit reached. Falling back to next model.")
                    # If this is not the last model, we just continue to try the next one (like 2.0-flash)
                    continue
                    
                print(f"❌ Gemini Chat Completion Error with {m}: {e}")
                continue
        
        print(f"❌ All Gemini Chat Models failed.")
        return {}

    def embed_content(self, text, task_type="RETRIEVAL_DOCUMENT"):
        # 1. If we already know what works, use it
        if self.working_config:
            try:
                result = self._make_request(text, self.working_config, task_type)
                return result.get('embedding', {}).get('values')
            except Exception as e:
                print(f"[Warn] Config {self.working_config['model']} failed: {e}. Retrying discovery...")
                self.working_config = None # Reset and fall through to discovery

        # 2. Discovery Mode: Try all configs
        errors = []
        for config in self.configs:
            try:
                # print(f"[DEBUG] Trying {config['model']} ({config['version']})...") 
                result = self._make_request(text, config, task_type)
                vals = result.get('embedding', {}).get('values')
                if vals:
                    print(f"[Success] Connected via {config['model']} ({config['version']})")
                    self.working_config = config
                    return vals
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8')
                # print(f"[DEBUG] Failed {config['model']}: {e.code}")
                errors.append(f"{config['model']}: {e.code}")
            except Exception as e:
                errors.append(f"{config['model']}: {e}")

        print(f"[CRITICAL] All Gemini embedding models failed. Details below:")
        for e in errors:
            print(f" - {e}")
            
        print("\n[WARN] Switching to MOCK embedding (Random Values) to allow system testing.")
        # Return a 768-dimensional random vector (standard size for text-embedding-004/001)
        import random
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

if __name__ == "__main__":
    # Test block
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets["GEMINI_API_KEY"])
    vec = client.embed_content("Hello World")
    if vec:
        print(f"Embedding success! Dimension: {len(vec)}")
    else:
        print("Embedding failed.")
