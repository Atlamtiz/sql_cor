import requests
import json
import openai

# https://console.bce.baidu.com/qianfan/overview 百度千帆 个人 API 
API_KEY = "l0nJttiqCgwgQdRoe8Jr8byS"
SECRET_KEY = "MNgcfGOnD7zSyPxqylsT02JK6mE7qG9J"

def get_access_token(API_KEY, SECRET_KEY):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def llama3_70b(prompt):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_3_70b?access_token=" + get_access_token(API_KEY, SECRET_KEY)

    response = requests.request(
        "POST",
        url,
        params = {
            'temperature': 0,
            'top_k': 1,
            'top_p': 1
        },
        headers = {
        'Content-Type': 'application/json'
        },
        data = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            },
            ]
        })
    )

    response = json.loads(response.text)
    return(response['result'])

def llama3_8b(prompt):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_3_8b?access_token=" + get_access_token(API_KEY, SECRET_KEY)

    response = requests.request(
        "POST",
        url,
        params = {
            'temperature': 0,
            'top_k': 1,
            'top_p': 1
        },
        headers = {
        'Content-Type': 'application/json'
        },
        data = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            },
            ]
        })
    )

    response = json.loads(response.text)
    return(response['result'])


# https://www.closeai-asia.com/account/billing/ 第三方 API 供应商

def gpt_4o_mini(prompt):
    openai.api_base = 'https://api.openai-proxy.org/v1'
    openai.api_key = 'sk-fgNlsY0Vz10Drr1F5MxEBI9TQbxgjMq75w1pvVIYVsrYcg0S'  # 个人 API
    response = openai.ChatCompletion.create(
        model = "gpt-4o-mini-2024-07-18",
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {"role": "user", "content": prompt}
        ],
        temperature = 0,
        top_p = 1
    )
    return response['choices'][0]['message']['content']


# https://bailian.console.aliyun.com/ 阿里平台
def qwen2_72b(prompt):
    openai.api_base = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    openai.api_key = 'sk-3a635441bb3e4467af5f3173f8eb0e7b' # 个人 API
    response = openai.ChatCompletion.create(
        model="qwen2-72b-instruct",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}],
        temperature=0,
        top_p=1
        )
    return response['choices'][0]['message']['content']

def qwen2_7b(prompt):
    openai.api_base = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    openai.api_key = 'sk-3a635441bb3e4467af5f3173f8eb0e7b' # 个人 API
    response = openai.ChatCompletion.create(
        model="qwen2-7b-instruct",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}],
        temperature=0,
        top_p=1
        )
    return response['choices'][0]['message']['content']
