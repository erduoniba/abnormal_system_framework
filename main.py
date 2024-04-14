import argparse
import os
import time
from system_framework import system_frameworks_list, get_system_frame_platforms
from min_os_version import read_minimum_os_version


def arg_parse():
    # 参数解析开始
    parser = argparse.ArgumentParser(description="自动分析 App 中依赖系统库版本和当前 App 最低系统版本是否一致")
    # 添加参数
    parser.add_argument("-f", "--file", help="要处理的 App 文件路径，注意不是 .ipa 文件的路径，而是 .app 路径",
                        required=True)
    parser.add_argument("-o", "--output", help="日志输出路径")
    # 解析命令行参数
    args = parser.parse_args()
    # 获取参数值
    app_path = args.file

    output = args.output
    if output is None:
        output = os.path.dirname(app_path)
    return app_path, output


def main():
    start_time = time.time()

    app_path, output = arg_parse()
    print("==Step1 解析参数")
    print("\tapp_path: " + app_path)
    print("\toutput: " + output)

    print("\n==Step2 通过 sh 脚本获取该 app 依赖的系统库列表（剔除 weak 依赖)）")
    frameworks = system_frameworks_list(app_path)
    print(f"\t系统库列表: {frameworks}")

    print("\n==Step3 读取 info.plist 文件获取该 app 版本信息")
    min_os_version, app_version, app_build = read_minimum_os_version(app_path)
    print(f"\tapp_version:{app_version} \tapp_build:{app_build}\tmin_ios_version:{min_os_version} ")

    print("\n==Step4 developer.apple.com查询获取系统库最低支持版本号，得到异常依赖")
    min_frameworks = get_system_frame_platforms(frameworks, min_os_version)
    if len(min_frameworks) > 0:
        print(f"\t异常依赖：{min_frameworks}\n\t!!!请重点排查!!!，不然可能导致低版本系统启动崩溃")
    else:
        print("正常依赖，请保持")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n本次分析耗时:{elapsed_time:.3f}秒")


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
