import os
import requests
import sys
import time

def download_file(url, destination, max_retries=5, timeout=600):
    for retry in range(max_retries):
        print(f"Download attempt {retry+1}/{max_retries}: {url} to {destination}")
        try:
            # 添加请求头，模拟浏览器行为
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 添加额外的重试机制并关闭SSL验证
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('https://', adapter)
            session.mount('http://', adapter)
            response = session.get(url, stream=True, timeout=timeout, headers=headers, verify=False)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            sys.stdout.write(f'\rProgress: {progress:.2f}%')
                            sys.stdout.flush()
            
            print(f"\nDownload completed: {destination}")
            return True
        except Exception as e:
            print(f"\nDownload failed on attempt {retry+1}: {str(e)}")
            if retry < max_retries - 1:
                wait_time = 2 ** retry  # 指数退避
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"All {max_retries} download attempts failed.")
    return False

# 使用Comfy-Org推荐的模型URL
model_url = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly-fp16.safetensors"
destination = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "checkpoints", "v1-5-pruned-emaonly-fp16.safetensors")

if __name__ == "__main__":
    print("尝试使用Python requests下载模型文件...")
    success = download_file(model_url, destination)
    
    if not success:
        print("\n=== 下载失败 ===")
        print("请尝试以下替代方法：")
        print("\n方法1：使用PowerShell下载")
        print(f"打开PowerShell并执行：")
        print(f"Invoke-WebRequest -Uri '{model_url}' -OutFile '{destination}' -UseBasicParsing")
        print("\n方法2：手动下载")
        print(f"1. 在浏览器中打开：{model_url}")
        print(f"2. 将文件保存到：{destination}")
        print("\n方法3：使用wget（如果已安装）")
        print(f"wget {model_url} -O {destination}")
        print("\n方法4：使用其他镜像站点")
        print("尝试从替代镜像下载：")
        print("https://civitai.com/api/download/models/131362")
        print("然后将文件重命名为：v1-5-pruned-emaonly-fp16.safetensors")
        print(f"并保存到：{destination}")
