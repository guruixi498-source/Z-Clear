import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("ILMU_API_KEY"),
    base_url=os.getenv("ILMU_API_BASE")
)

print("正在探测 API Key 的有效性及可用模型...")
try:
    models = client.models.list()
    print("✅ 探测成功！当前 API Key 支持以下模型：")
    for m in models.data:
        print(f"  - {m.id}")
except Exception as e:
    print("❌ 获取模型列表失败，错误信息：", e)

print("-" * 40)
print("正在进行基础对话测试 (使用 ilmu-glm-5.1)...")
try:
    response = client.chat.completions.create(
        model="ilmu-glm-5.1",
        messages=[{"role": "user", "content": "Hello, simply reply 'OK'"}],
        timeout=15  # 设置15秒超时
    )
    print("✅ 对话测试成功！返回内容：", response.choices[0].message.content)
except Exception as e:
    print("❌ 对话测试失败，错误信息：", e)
