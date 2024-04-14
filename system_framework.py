import os
import subprocess
import re
import requests
import json


def system_frameworks_list(app_path):
    filename = os.path.basename(app_path)
    filename, extension = os.path.splitext(filename)
    macho_path = app_path + "/" + filename
    result = subprocess.run(["sh", "otool.sh", macho_path], stdout=subprocess.PIPE)
    # 检查命令是否成功执行
    if result.returncode == 0:
        # 将输出解码为字符串
        output_str = result.stdout.decode('utf-8')

        # 打印输出
        print("\t执行 sh 脚本获取系统列表信息成功")
        frameworks = extract_frameworks(output_str)
        return frameworks
    else:
        print(f"\t执行脚本失败，退出状态码：{result.returncode}")
        return None


def extract_frameworks(output_str):
    frameworks = []
    framework_pattern = r"/System/Library/Frameworks/(.+?)\.framework"
    for line in output_str.splitlines():
        match = re.search(framework_pattern, line)
        if match and ('weak' in line) == False:
            framework_path = match.group(1)
            frameworks.append(framework_path)
    return frameworks


def get_platforms_data(url):
    """
    请求页面并解析 JSON 数据，获取平台数据
    Args:
        url: 要请求的页面 URL
    Returns:
        平台数据列表，每个元素为一个字典，包含平台名称、引入版本和最新版本
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content)
        platforms_data = data['metadata']['platforms']
        return platforms_data
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None


def get_system_frame_platforms(frameworks, min_os_version):
    min_frameworks = {}
    for framework in frameworks:
        url = f'https://developer.apple.com/tutorials/data/documentation/{framework}.json'
        platforms_data = get_platforms_data(url)

        if platforms_data:
            for platform in platforms_data:
                introduced = platform['introducedAt']
                if platform['name'] == "iOS" and float(introduced) > float(min_os_version):
                    min_frameworks[framework] = platform['introducedAt']
        else:
            min_frameworks[framework] = "None"
            print(f"{framework} 获取平台数据失败")
    return min_frameworks
