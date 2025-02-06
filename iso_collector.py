import os
import json
import platform
import subprocess


def extract_packages_from_iso(iso_path=None, output_file="target_system.json"):
    """
    Extract RPM package names, versions, dependencies, and file lists from ISO (Linux).
    :param iso_path: Path to the ISO file (for Linux).
    :param output_file: Path to the output JSON file.
    """
    package_list = []

    if platform.system() == "Linux":
        # 使用系统自动挂载路径
        packages_dir = "/run/media/kylin/CentOS 7 x86_64/Packages"
        if not os.path.exists(packages_dir):
            print(f"Packages directory not found at {packages_dir}.")
            return

        # 提取软件包信息
        try:
            for file_name in os.listdir(packages_dir):
                if file_name.endswith(".rpm"):
                    try:
                        rpm_path = os.path.join(packages_dir, file_name)
                        # 提取包名和版本
                        parts = file_name.split("-")
                        name = "-".join(parts[:-2])  # Everything before version-release
                        version = parts[-2]  # The version part

                        # 使用 rpm 命令提取依赖信息
                        dependencies = subprocess.run(
                            ["rpm", "-qpR", rpm_path],
                            stdout=subprocess.PIPE,
                            text=True,
                            encoding="utf-8"
                        ).stdout.split("\n")

                        # 使用 rpm 命令提取文件列表
                        files = subprocess.run(
                            ["rpm", "-qpl", rpm_path],
                            stdout=subprocess.PIPE,
                            text=True,
                            encoding="utf-8"
                        ).stdout.split("\n")

                        # 将包信息添加到列表
                        package_list.append({
                            "name": name,
                            "version": version,
                            "dependencies": dependencies,
                            "files": files
                        })
                    except Exception as e:
                        print(f"Error processing RPM file {file_name}: {e}")
        except Exception as e:
            print(f"Error processing Packages directory: {e}")

    else:
        print("This script is only supported on Linux.")
        return

    # 保存提取到的数据到 JSON 文件
    try:
        with open(output_file, "w") as json_file:
            json.dump({"software_packages": package_list}, json_file, indent=4)
        print(f"Packages extracted and saved to {output_file}.")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


# 示例用法
if __name__ == "__main__":
    if platform.system() == "Linux":
        # 替换为实际的 ISO 挂载路径
        iso_path = "/run/media/kylin/CentOS 7 x86_64"
        extract_packages_from_iso(iso_path=iso_path, output_file="source_system.json")
