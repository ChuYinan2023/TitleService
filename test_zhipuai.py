from zhipuai import ZhipuAI
import os

def test_zhipuai_api():
    # 直接在代码中设置环境变量
    os.environ['ZHIPUAI_API_KEY'] = 'e8d5a4cd0a1d496de21ed08c64268a85.H8YYYahnU4CRGq8X'  # 请替换为你的实际 API Key

    # 详细检查环境变量
    print("=== 环境变量诊断 ===")
    print(f"原始环境变量值: '{os.environ.get('ZHIPUAI_API_KEY', '')}'")
    print(f"去除空白的环境变量值: '{os.environ.get('ZHIPUAI_API_KEY', '').strip()}'")
    print(f"环境变量是否为空: {not os.environ.get('ZHIPUAI_API_KEY', '')}")
    print(f"环境变量长度: {len(os.environ.get('ZHIPUAI_API_KEY', ''))}")

    # 从环境变量获取API Key
    api_key = os.environ.get('ZHIPUAI_API_KEY', '').strip()
    if not api_key:
        print("请设置 ZHIPUAI_API_KEY 环境变量")
        return

    # 初始化客户端
    client = ZhipuAI(api_key=api_key)

    try:
        # 文本生成测试
        print("==== 文本生成测试 ====")
        text_response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=[
                {
                    "role": "user", 
                    "content": "用一段有趣的话介绍人工智能"
                }
            ],
            top_p=0.7,
            temperature=0.9,
            max_tokens=256,
            stream=False
        )
        print("文本生成结果:")
        print(text_response.choices[0].message.content)
        
        # 图像描述测试 (使用占位符图片URL)
        print("\n==== 图像描述测试 ====")
        image_response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请仔细描述这个图片"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://example.com/sample_image.jpg"  # 替换为实际图片URL
                            }
                        }
                    ]
                }
            ],
            top_p=0.7,
            temperature=0.95,
            max_tokens=1024,
            stream=False
        )
        print("图像描述结果:")
        print(image_response.choices[0].message.content)
        
    except Exception as e:
        print("API调用发生错误:")
        print(str(e))

if __name__ == "__main__":
    test_zhipuai_api()
