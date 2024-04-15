import os
import subprocess
import re
import requests
import json


def ignore_frameworks():
    # OpenAL（Open Audio Library）是一个跨平台的开放源代码音频库，它提供了一组接口，
    # 使得游戏开发者能够更方便地处理音频。
    # OpenAL 提供了诸如3D声音定位、回声效果、混响效果等功能，使得游戏开发者能够创建更加逼真的音效体验。
    # https://www.openal.org/platforms/ 查询得到 iOS 开发中是在 Core Audio 中，而 Core Audio从 iOS2就开始支持

    # MobileCoreServices框架使用统一类型标识符（UTI）信息来创建和操作可以在您的应用和其他应用和服务之间交换的数据。
    # 底层直接引用 CoreServices，MobileCoreServices支持
    # 支持的最低系统版本，这个框架自 iOS 的早期版本就已经存在，并且随着操作系统的每次更新而得到更新和维护

    # WebKit 和 JavaScriptCore 在 iOS7就开始支持，但是有一些特性API会有版本限制，不再系统库这一层级去考虑
    return ["OpenAL", "MobileCoreServices", "WebKit", "JavaScriptCore"]


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
    ignores = ignore_frameworks()
    framework_pattern = r"/System/Library/Frameworks/(.+?)\.framework"
    for line in output_str.splitlines():
        ignore_tag = False
        for ignore in ignores:
            if ignore in line:
                ignore_tag = True
                break
        if ignore_tag:
            continue
        if 'weak' in line:
            continue
        match = re.search(framework_pattern, line)
        if match:
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
