import requests
import openai
import anthropic

from src.utils import logging


CLIENT_CACHE = {}
API_PROVIDERS = {
    "together": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer 5cf1fef634f75fd5b88e3e9d84bb0ee3b5dba303c05468ea02a85d63f22aa2bb",
        },
    },
    "webui": {
        "url": "https://7fc6-192-222-54-57.ngrok-free.app/v1/chat/completions",
        "headers": {
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    },
}


def get_client(provider, config_data):
    if provider not in CLIENT_CACHE:
        if provider == "openai":
            CLIENT_CACHE[provider] = openai.OpenAI(
                api_key=config_data["test"]["openai_key"]
            )
        elif provider == "anthropic":
            CLIENT_CACHE[provider] = anthropic.Anthropic(
                api_key=config_data["test"]["ANTHROPIC_API_KEY"]
            )
    return CLIENT_CACHE.get(provider)


def get_response(config_data, api_provider, model_params, messages):
    api_provider = config_data["intent_detection"]["api_provider"]
    if api_provider == "webui":
        payload = {
            "messages": messages,
            "mode": "instruct",
            "max_new_tokens": config_data["max_tokens"],
            **{k: v for k, v in model_params.items() if k in ["model", "top_p", "max_tokens", "temperature"]}
        }
        api_info = API_PROVIDERS[api_provider]
        response = requests.post(
            api_info["url"], json=payload, headers=api_info["headers"]
        ).json()
        return response["choices"][0]["message"]["content"]
    elif api_provider in "together":
        payload = {
            "messages": messages,
            **{k: v for k, v in model_params.items() if k in ["model", "top_p", "max_tokens", "temperature"]}
        }
        api_info = API_PROVIDERS[api_provider]
        response = requests.post(
            api_info["url"], json=payload, headers=api_info["headers"]
        ).json()
        return response["choices"][0]["message"]["content"]
    elif api_provider == "openai":
        payload = {
            "messages": messages,
            **{k: v for k, v in model_params.items() if k in ["model", "temperature"]},
        }
        client = get_client(api_provider, config_data)
        response = client.chat.completions.create(**payload)
        return response.choices[0].message.content
    elif api_provider == "anthropic":
        payload = {
            "messages": messages,
            **{
                model_param
                for model_param in model_params
                if model_param
                in [
                    "model",
                    "max_tokens",
                ]
            },
        }
        client = get_client(api_provider, config_data)
        payload["messages"][0]["role"] = "user"  # TODO: figure out why we do this
        response = client.messages.create(**payload)
        return response.choices[0].message.content
    else:
        raise ValueError(f"API provider {api_provider} not supported")


def get_completion(config_data, api_provider, model_params, messages):
    return get_response(config_data, api_provider, model_params, messages)


@logging.request_decorator
def get_completion_with_logs(config_data, _scenario_data, api_provider, model_params, messages, _request_type):
    return get_response(config_data, api_provider, model_params, messages)


@logging.request_decorator
def get_embeddings_with_logs(config_data, _scenario_data, input, model, _request_type):
    client = get_client("openai", config_data)
    response = client.embeddings.create(input=input, model=model)
    return response.data[0].embedding
