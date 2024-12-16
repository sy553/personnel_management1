import requests
import json

# API 端点
url = 'http://localhost:5000/api/salary/records/batch'

# 请求数据
data = {
    'year': 2024,
    'month': 12,
    'employee_ids': [1, 2, 3, 4, 5, 6]
}

# 发送请求
response = requests.post(url, json=data)

# 打印响应
print(f'状态码: {response.status_code}')
print('响应内容:')
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
