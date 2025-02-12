import os
import json
import platform
import subprocess

def extract_installed_packages(output_file="sourceinfo.json"):
    package_list = []

    if platform.system() == "Linux":
        try:
            # rpm -qa 获取所有已安装包
            result = subprocess.getoutput("rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}\\n'")
            for line in result.split("\n"):
                if line:
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        name, version = parts

                        # 提取依赖信息
                        dependencies = subprocess.run(
                            ["rpm", "-qR", name],
                            stdout=subprocess.PIPE,
                            text=True,
                            encoding="utf-8"
                        ).stdout.strip().split("\n")

                        # 提取文件列表
                        files = subprocess.run(
                            ["rpm", "-ql", name],
                            stdout=subprocess.PIPE,
                            text=True,
                            encoding="utf-8"
                        ).stdout.strip().split("\n")

                        package_list.append({
                            "name": name,
                            "version": version,
                            "dependencies": dependencies,
                            "files": files
                        })
        except Exception as e:
            print(f"Error collecting installed RPM packages: {e}")
    else:
        print("This script is only supported on Linux.")
        return

    # 写入 sourceinfo.json
    try:
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump({"software_packages": package_list}, json_file, indent=4, ensure_ascii=False)
        print(f"Installed packages extracted and saved to {output_file}.")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


def is_iso_mounted(mount_point):
    result = subprocess.run(["findmnt", mount_point], stdout=subprocess.PIPE, text=True)
    return result.returncode == 0


def extract_packages_from_iso(iso_path, output_file="targetinfo.json"):
    package_list = []
    mount_point = "/mnt/iso"

    os.makedirs(mount_point, exist_ok=True)
    iso_already_mounted = is_iso_mounted(mount_point)

    try:
        # 挂载ISO
        if not iso_already_mounted:
            subprocess.run(["sudo", "mount", "-o", "loop", iso_path, mount_point], check=True)

        packages_dir = os.path.join(mount_point, "Packages")
        if not os.path.exists(packages_dir):
            print(f"Error: Packages directory not found in {mount_point}.")
            return

        # 扫描所有rpm文件
        for file_name in os.listdir(packages_dir):
            if file_name.endswith(".rpm"):
                try:
                    rpm_path = os.path.join(packages_dir, file_name)
                    parts = file_name.rsplit("-", 2)
                    if len(parts) < 3:
                        print(f"Skipping invalid RPM file: {file_name}")
                        continue

                    name, version = parts[0], parts[1]

                    dependencies = subprocess.run(
                        ["rpm", "--nosignature", "-qpR", rpm_path],
                        stdout=subprocess.PIPE,
                        text=True,
                        encoding="utf-8"
                    ).stdout.strip().split("\n")

                    files = subprocess.run(
                        ["rpm", "--nosignature", "-qpl", rpm_path],
                        stdout=subprocess.PIPE,
                        text=True,
                        encoding="utf-8"
                    ).stdout.strip().split("\n")

                    package_list.append({
                        "name": name,
                        "version": version,
                        "dependencies": dependencies,
                        "files": files
                    })
                except Exception as e:
                    print(f"Error processing RPM file {file_name}: {e}")

    except Exception as e:
        print(f"Error processing ISO: {e}")
    finally:
        if not iso_already_mounted:
            subprocess.run(["sudo", "umount", mount_point], check=True)

    # 写入 targetinfo.json
    try:
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump({"software_packages": package_list}, json_file, indent=4, ensure_ascii=False)
        print(f"ISO packages extracted and saved to {output_file}.")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


if __name__ == "__main__":
    if platform.system() == "Linux":
        # 采集当前系统的 RPM 软件包信息 => sourceinfo.json
        extract_installed_packages(output_file="sourceinfo.json")

        # 采集 openEuler ISO 镜像的 RPM 软件包信息 => targetinfo.json
        iso_path = "/home/kylin/桌面/openEuler-24.03-LTS-SP1-x86_64-dvd.iso"
        extract_packages_from_iso(iso_path=iso_path, output_file="targetinfo.json")
