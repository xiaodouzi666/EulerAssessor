#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import platform
import subprocess
import re
from datetime import datetime

########################################
# 1. 配置区域
########################################

SOURCE_CONFIG_FILES = [
    "/etc/fstab",
    "/etc/ssh/sshd_config",
    "/etc/sysctl.conf",
    "/etc/yum.repos.d"
]

ISO_PACKAGES_DIR = "/mnt/iso/Packages"
COMMON_COMMANDS = ["bash","sh","python3.9","gcc","docker","git","java","systemctl"]


########################################
# 2. 采集逻辑 -- 源系统
########################################

def collect_source_info(output_file="source_all.json"):
    """
    一次性采集: 
      1) 配置文件 (config_files)
      2) 硬件和驱动信息 (hardware_info)
      3) 命令可用性 (commands)
      4) 系统基础信息 (os_info)
      5) 网络/服务/进程/磁盘/环境变量 等(与mock对应)
    """
    data = {}

    # 2.1 config_files
    data["config_files"] = collect_config_files(SOURCE_CONFIG_FILES)

    # 2.2 硬件和驱动
    data["hardware_info"] = collect_hardware_info_source()

    # 2.3 命令可用性
    data["commands"] = collect_commands_source()

    # 2.4 基本OS信息
    data["os_info"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture()[0]
    }

    # 2.5 额外: 网络/服务/进程/磁盘/环境变量
    if platform.system() == "Linux":
        data["network_info"] = subprocess.getoutput("ss -tuln")
        data["services_info"] = subprocess.getoutput("systemctl list-units --type=service --state=running")
        data["processes"] = subprocess.getoutput("ps -aux")
        data["disk_info"] = subprocess.getoutput("lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT")
        data["environment_variables"] = dict(os.environ)
    else:
        # 如果是Windows或其他系统，可以自行处理
        data["network_info"] = "N/A"
        data["services_info"] = "N/A"
        data["processes"] = "N/A"
        data["disk_info"] = "N/A"
        data["environment_variables"] = {}

    # 写出 source_all.json
    with open(output_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)
    print(f"[collect_source_info] Wrote all info to {output_file}")


def collect_config_files(paths):
    results = []
    for path in paths:
        if not os.path.exists(path):
            results.append({
                "file_path": path,
                "exists": False,
                "is_directory": False,
                "content_lines": [],
                "mode": None,
                "mtime": None,
                "size": None
            })
            continue

        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    results.append(read_single_file(full_path))
        else:
            results.append(read_single_file(path))
    return results


def read_single_file(path):
    info = {
        "file_path": path,
        "exists": True,
        "is_directory": False,
        "content_lines": [],
        "mode": None,
        "mtime": None,
        "size": None
    }
    try:
        st = os.stat(path)
        info["mode"] = oct(st.st_mode & 0o777)
        info["mtime"] = datetime.fromtimestamp(st.st_mtime).isoformat()
        info["size"] = st.st_size

        if os.path.isdir(path):
            info["is_directory"] = True
            return info

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        info["content_lines"] = [ln.rstrip("\n") for ln in lines]
    except Exception as e:
        info["content_lines"] = [f"[Error reading: {e}]"]
    return info


def collect_hardware_info_source():
    """
    在源系统获取 lspci, lsusb, lsmod 等信息
    """
    if platform.system() != "Linux":
        return {"error":"Not a Linux system, skipping hardware_info"}

    hardware_data = {
        "pci_devices": [],
        "usb_devices": [],
        "loaded_modules": []
    }

    # lspci
    lspci_out = subprocess.getoutput("lspci")
    for line in lspci_out.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^([0-9a-fA-F:.]+)\s+(.*)$", line)
        if match:
            hardware_data["pci_devices"].append({
                "bus_id": match.group(1),
                "description": match.group(2)
            })
    # lsusb
    lsusb_out = subprocess.getoutput("lsusb")
    if lsusb_out:
        usb_list = []
        for line in lsusb_out.split("\n"):
            if line.strip():
                usb_list.append(line.strip())
        hardware_data["usb_devices"] = usb_list
    # lsmod
    lsmod_out = subprocess.getoutput("lsmod")
    lines = lsmod_out.split("\n")
    if len(lines) > 1:
        loaded_mods = []
        for ln in lines[1:]:
            cols = ln.split()
            if len(cols) >= 1:
                loaded_mods.append(cols[0])
        hardware_data["loaded_modules"] = loaded_mods

    return hardware_data


def collect_commands_source():
    cmd_info_list = []
    for cmd in COMMON_COMMANDS:
        info = {
            "name": cmd,
            "exists": False,
            "which_path": "",
            "version_info": ""
        }
        try:
            res = subprocess.run(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                info["exists"] = True
                info["which_path"] = res.stdout.strip()
                ver_res = subprocess.run([cmd,"--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                first_line = ver_res.stdout.split("\n")[0].strip()
                info["version_info"] = first_line
        except:
            pass
        cmd_info_list.append(info)
    return cmd_info_list


########################################
# 3. 采集逻辑 -- 目标系统(ISO静态分析)
########################################

def collect_target_info(iso_packages_dir=ISO_PACKAGES_DIR, output_file="target_all.json"):
    """
    在 ISO 中用 rpm -qpl 等方式做静态分析:
      - config_files (文件存在性)
      - hardware_info (内核模块)
      - commands ( /usr/bin/xxx )
      - os_info (简单占位)
      - network_info / services_info / processes / disk_info / environment_variables => 无法真实获取, 写占位
    """
    data = {}

    # 3.1 config_files
    data["config_files"] = collect_config_files_target(iso_packages_dir, SOURCE_CONFIG_FILES)

    # 3.2 硬件驱动 => 收集 .ko
    data["hardware_info"] = collect_hardware_info_target(iso_packages_dir)

    # 3.3 命令可用性 => rpm中是否含 /usr/bin/xxx
    data["commands"] = collect_commands_target(iso_packages_dir)

    # 3.4 os_info 占位
    data["os_info"] = {
        "system": "openEuler",
        "release": "24.03-LTS-SP1",
        "version": "unknown",
        "architecture": "x86_64"
    }

    # 3.5 其他字段 (mock中有), 这里无法真实采集, 填写占位
    data["network_info"] = "tcp LISTEN 0 128 0.0.0.0:22 ...\ntcp LISTEN 0 128 :::22 ..."
    data["services_info"] = "UNIT                     LOAD   ACTIVE SUB     DESCRIPTION\nsshd.service             loaded active running OpenSSH server daemon"
    data["processes"] = "root       1  0.0  0.1  19344  1612 ?  Ss   00:00:01 /usr/lib/systemd/systemd\n..."
    data["disk_info"] = "NAME  FSTYPE  SIZE MOUNTPOINT\nsda   xfs     60G  /\nsr0   iso9660 4.3G /mnt/iso"
    data["environment_variables"] = {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin",
        "HOME": "/root",
        "LANG": "en_US.UTF-8"
    }

    # 写出 target_all.json
    with open(output_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)
    print(f"[collect_target_info] Wrote all info to {output_file}")


def collect_config_files_target(packages_dir, source_config_list):
    results = []
    for conf_path in source_config_list:
        if os.path.isdir(conf_path):
            file_list = []
            for root, dirs, files in os.walk(conf_path):
                for fname in files:
                    file_list.append(os.path.join(root, fname))
            for p in file_list:
                results.append(check_config_in_rpms(p, packages_dir))
        else:
            results.append(check_config_in_rpms(conf_path, packages_dir))
    return results


def check_config_in_rpms(conf_path, packages_dir):
    if not conf_path.startswith("/"):
        conf_full = "/" + conf_path
    else:
        conf_full = conf_path

    info = {
        "file_path": conf_full,
        "exists": False,
        "found_in_rpms": []
    }

    rpms = [f for f in os.listdir(packages_dir) if f.endswith(".rpm")]
    total_rpms = len(rpms)
    print(f"[check_config_in_rpms] Checking {conf_path} in {total_rpms} RPMs...")

    for i, rpm_name in enumerate(rpms, start=1):
        print(f"  -> ({i}/{total_rpms}) Checking {rpm_name}")
        rpm_path = os.path.join(packages_dir, rpm_name)
        try:
            res = subprocess.run(["rpm", "--nosignature", "-qpl", rpm_path],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                lines = res.stdout.split("\n")
                if conf_full in lines:
                    info["exists"] = True
                    info["found_in_rpms"].append(rpm_name)
        except:
            pass
    return info


def collect_hardware_info_target(packages_dir):
    data = {"kernel_modules": []}
    modules_set = set()
    rpms = [f for f in os.listdir(packages_dir) if f.endswith(".rpm")]
    total_rpms = len(rpms)

    print(f"[collect_hardware_info_target] Found {total_rpms} RPMs. Checking for .ko files...")

    for i, rpm_name in enumerate(rpms, start=1):
        print(f"  -> ({i}/{total_rpms}) Analyzing {rpm_name}")
        rpm_path = os.path.join(packages_dir, rpm_name)
        try:
            res = subprocess.run(["rpm","--nosignature","-qpl",rpm_path],
                                 stdout=subprocess.PIPE, text=True)
            file_list = res.stdout.strip().split("\n")
            for fp in file_list:
                if fp.endswith(".ko"):
                    modules_set.add(os.path.basename(fp))
        except:
            pass

    data["kernel_modules"] = sorted(list(modules_set))
    return data


def collect_commands_target(packages_dir):
    possible_paths = []
    for c in COMMON_COMMANDS:
        possible_paths.append(f"/bin/{c}")
        possible_paths.append(f"/usr/bin/{c}")
        possible_paths.append(f"/usr/sbin/{c}")
        possible_paths.append(f"/usr/local/bin/{c}")

    cmd_map = {c:{"name":c,"exists":False,"found_in_rpms":[]} for c in COMMON_COMMANDS}

    rpms = [f for f in os.listdir(packages_dir) if f.endswith(".rpm")]
    total_rpms = len(rpms)

    print(f"[collect_commands_target] Found {total_rpms} RPMs. Checking commands...")

    for i, rpm_name in enumerate(rpms, start=1):
        print(f"  -> ({i}/{total_rpms}) Checking {rpm_name}")
        rpm_path = os.path.join(packages_dir, rpm_name)
        try:
            res = subprocess.run(["rpm","--nosignature","-qpl",rpm_path],
                                 stdout=subprocess.PIPE, text=True)
            file_list = res.stdout.strip().split("\n")
            for c in COMMON_COMMANDS:
                if not cmd_map[c]["exists"]:
                    for p in possible_paths:
                        if p in file_list:
                            cmd_map[c]["exists"] = True
                            cmd_map[c]["found_in_rpms"].append(rpm_name)
        except:
            pass

    return list(cmd_map.values())


########################################
# 4. 差异分析 => all_diff.json
########################################

def compare_all(source_json="source_all.json", target_json="target_all.json", diff_json="all_diff.json"):
    """
    对比 source_all.json 和 target_all.json:
      - config_diff
      - hardware_diff
      - command_diff
    输出 all_diff.json
    """
    try:
        with open(source_json, "r", encoding="utf-8") as sf:
            source_data = json.load(sf)
        with open(target_json, "r", encoding="utf-8") as tf:
            target_data = json.load(tf)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    diff_result = {
        "config_diff": compare_config_section(source_data.get("config_files",[]), 
                                              target_data.get("config_files",[])),
        "hardware_diff": compare_hardware_section(source_data.get("hardware_info",{}), 
                                                  target_data.get("hardware_info",{})),
        "command_diff": compare_command_section(source_data.get("commands",[]),
                                                target_data.get("commands",[]))
    }

    with open(diff_json, "w", encoding="utf-8") as jf:
        json.dump(diff_result, jf, indent=4, ensure_ascii=False)
    print(f"[compare_all] Done => {diff_json}")


def compare_config_section(src_config, tgt_config):
    src_map = { item["file_path"] : item for item in src_config }
    diff = {
        "missing_in_target": [],
        "found_in_target": [],
        "content_note": "Target only provides file path existence (no actual content)."
    }
    tgt_map = { item["file_path"] : item for item in tgt_config }

    for spath, sitem in src_map.items():
        if not sitem["exists"]:
            continue
        titem = tgt_map.get(spath)
        if titem is None:
            diff["missing_in_target"].append(spath)
        else:
            if not titem["exists"]:
                diff["missing_in_target"].append(spath)
            else:
                diff["found_in_target"].append({
                    "file_path": spath,
                    "found_in_rpms": titem["found_in_rpms"]
                })
    return diff


def compare_hardware_section(src_hw, tgt_hw):
    diff = {
        "missing_modules_in_target": [],
        "extra_modules_in_target": []
    }
    src_mods = set(src_hw.get("loaded_modules",[]))
    tgt_mods = set(tgt_hw.get("kernel_modules",[]))
    diff["missing_modules_in_target"] = list(src_mods - tgt_mods)
    diff["extra_modules_in_target"] = list(tgt_mods - src_mods)
    return diff


def compare_command_section(src_cmds, tgt_cmds):
    src_map = { c["name"]: c for c in src_cmds }
    tgt_map = { c["name"]: c for c in tgt_cmds }

    diff = {
        "missing_in_target": [],
        "found_in_target": [],
        "version_info_note": "Target side no real version (just presence)."
    }

    for name, sitem in src_map.items():
        titem = tgt_map.get(name)
        if not titem:
            if sitem["exists"]:
                diff["missing_in_target"].append(name)
        else:
            if sitem["exists"] and not titem["exists"]:
                diff["missing_in_target"].append(name)
            elif sitem["exists"] and titem["exists"]:
                diff["found_in_target"].append({
                    "name": name,
                    "source_version": sitem["version_info"],
                    "found_in_rpms": titem["found_in_rpms"]
                })
    return diff


########################################
# 5. 命令行入口
########################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3.9 collect_and_compare_all.py source [output_file]")
        print("  python3.9 collect_and_compare_all.py target [output_file]")
        print("  python3.9 collect_and_compare_all.py compare [source_json] [target_json] [diff_json]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "source":
        out = sys.argv[2] if len(sys.argv)>2 else "source_all.json"
        collect_source_info(out)
    elif cmd == "target":
        out = sys.argv[2] if len(sys.argv)>2 else "target_all.json"
        collect_target_info(ISO_PACKAGES_DIR, out)
    elif cmd == "compare":
        src = sys.argv[2] if len(sys.argv)>2 else "source_all.json"
        tgt = sys.argv[3] if len(sys.argv)>3 else "target_all.json"
        diff = sys.argv[4] if len(sys.argv)>4 else "all_diff.json"
        compare_all(src, tgt, diff)
    else:
        print("Unknown command:", cmd)
