import os
import requests
import sys
import time
import argparse

def download_file(url, destination, max_retries=5, timeout=600):
    """下载单个文件"""
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
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
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

def download_missing_models():
    """下载所有缺失的模型文件"""
    # 定义ComfyUI主目录
    comfyui_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义模型下载信息（URL需要根据实际情况补充）
    models_to_download = [
        # VAE模型
        {
            'name': 'hunyuan_video_vae_bf16.safetensors',
            'type': 'vae',
            'url': 'https://huggingface.co/tencent/HunyuanVideo/resolve/main/hunyuan_video_vae_bf16.safetensors',  # 示例URL
            'destination': os.path.join(comfyui_dir, 'models', 'vae', 'hunyuan_video_vae_bf16.safetensors')
        },
        # CLIP模型1
        {
            'name': 'clip_l.safetensors',
            'type': 'clip',
            'url': 'https://huggingface.co/tencent/HunyuanVideo/resolve/main/clip_l.safetensors',  # 示例URL
            'destination': os.path.join(comfyui_dir, 'models', 'clip', 'clip_l.safetensors')
        },
        # CLIP模型2
        {
            'name': 'qwen_2.5_vl_7b_fp8_scaled.safetensors',
            'type': 'clip',
            'url': 'https://huggingface.co/tencent/HunyuanVideo/resolve/main/qwen_2.5_vl_7b_fp8_scaled.safetensors',  # 示例URL
            'destination': os.path.join(comfyui_dir, 'models', 'clip', 'qwen_2.5_vl_7b_fp8_scaled.safetensors')
        },
        # UNET模型
        {
            'name': 'kandinsky5lite_i2v_5s.safetensors',
            'type': 'unet',
            'url': 'https://huggingface.co/tencent/HunyuanVideo/resolve/main/kandinsky5lite_i2v_5s.safetensors',  # 示例URL
            'destination': os.path.join(comfyui_dir, 'models', 'unet', 'kandinsky5lite_i2v_5s.safetensors')
        }
    ]
    
    print("=== 开始下载缺失的模型文件 ===")
    
    for model_info in models_to_download:
        print(f"\n正在下载 {model_info['name']}...")
        
        # 检查文件是否已存在
        if os.path.exists(model_info['destination']):
            print(f"文件 {model_info['name']} 已存在，跳过下载")
            continue
        
        success = download_file(model_info['url'], model_info['destination'])
        
        if not success:
            print(f"\n=== 下载失败: {model_info['name']} ===")
            print("请尝试以下替代方法：")
            print("\n方法1：使用PowerShell下载")
            print(f"打开PowerShell并执行：")
            print(f"Invoke-WebRequest -Uri '{model_info['url']}' -OutFile '{model_info['destination']}' -UseBasicParsing")
            print("\n方法2：手动下载")
            print(f"1. 在浏览器中打开：{model_info['url']}")
            print(f"2. 将文件保存到：{model_info['destination']}")
            print("\n方法3：使用wget（如果已安装）")
            print(f"wget {model_info['url']} -O {model_info['destination']}")
            print("\n请确保文件正确放置在以下目录：")
            print(f"VAE模型 -> {os.path.join(comfyui_dir, 'models', 'vae')}")
            print(f"CLIP模型 -> {os.path.join(comfyui_dir, 'models', 'clip')}")
            print(f"UNET模型 -> {os.path.join(comfyui_dir, 'models', 'unet')}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ComfyUI模型下载工具")
    parser.add_argument('--all', action='store_true', help='下载所有缺失的模型文件')
    parser.add_argument('--url', type=str, help='指定单个模型的下载URL')
    parser.add_argument('--destination', type=str, help='指定单个模型的保存路径')
    args = parser.parse_args()
    
    if args.all:
        download_missing_models()
    elif args.url and args.destination:
        print("尝试使用Python requests下载指定模型文件...")
        success = download_file(args.url, args.destination)
        if not success:
            print("\n=== 下载失败 ===")
    else:
        # 默认下载stable-diffusion-v1-5模型
        model_url = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly-fp16.safetensors"
        destination = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "checkpoints", "v1-5-pruned-emaonly-fp16.safetensors")
        
        print("尝试使用Python requests下载Stable Diffusion v1.5模型文件...")
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

if __name__ == "__main__":
    main()
