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
# 1. 配置区域：需根据实际情况可自定义的全局常量
########################################

# 源系统要采集的关键配置文件(真实环境)
SOURCE_CONFIG_FILES = [
    "/etc/fstab",
    "/etc/ssh/sshd_config",
    "/etc/sysctl.conf",
    "/etc/yum.repos.d"  # 如果是目录，会递归处理
]

# 目标系统ISO中Packages目录位置
ISO_PACKAGES_DIR = "/mnt/iso/Packages"

# 常用命令列表
COMMON_COMMANDS = ["bash","sh","python3","gcc","docker","git","java","systemctl"]


########################################
# 2. 采集逻辑 -- 源系统
########################################

def collect_source_info(output_file="source_all.json"):
    """
    一次性采集 '配置文件内容+属性'、'硬件/驱动信息'、'命令可用性'，并输出到单个 JSON.
    在真实的源系统(CentOS)上执行。
    """
    data = {}

    # 2.1 采集配置文件
    data["config_files"] = collect_config_files(SOURCE_CONFIG_FILES)

    # 2.2 硬件和驱动信息
    data["hardware_info"] = collect_hardware_info_source()

    # 2.3 命令可用性
    data["commands"] = collect_commands_source()

    # 2.4 其他系统信息(可自由扩展)
    data["os_info"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture()[0]
    }

    # 写出结果
    with open(output_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)
    print(f"[collect_source_info] Wrote all info to {output_file}")


def collect_config_files(paths):
    """
    收集源系统里指定的配置文件或目录，返回一个 list[dict], 每个元素记录内容/属性
    """
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
            # 目录 => 递归处理其中的所有文件
            for root, dirs, files in os.walk(path):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    results.append( read_single_file(full_path) )
        else:
            # 单文件
            results.append( read_single_file(path) )
    return results


def read_single_file(path):
    """
    读取文件的内容和属性，返回字典
    """
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
    """
    在源系统真实执行 'which cmd' + '--version', 返回命令可用性与版本信息
    """
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
    由于在ISO中无法直接执行命令/访问/etc,只能基于 rpm -qpl 等静态分析:
    - 配置文件(仅判断路径是否存在)
    - 驱动(内核模块 .ko)
    - 命令文件(/usr/bin/xxx /bin/xxx等)
    """
    data = {}

    # 3.1 分析关键配置文件(仅能得知有没有)
    data["config_files"] = collect_config_files_target(iso_packages_dir, SOURCE_CONFIG_FILES)

    # 3.2 硬件驱动 => 看 .ko 文件
    data["hardware_info"] = collect_hardware_info_target(iso_packages_dir)

    # 3.3 命令可用性 => 看 /usr/bin/<cmd> 是否在 rpm 文件列表
    data["commands"] = collect_commands_target(iso_packages_dir)

    # 3.4 也可加 "os_info" => 读取 iso 里 repodata/xxx
    data["os_info"] = {
        "system": "openEuler (from ISO)",
        "release": "unknown",
        "version": "unknown",
        "architecture": "x86_64"
    }

    with open(output_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=4, ensure_ascii=False)
    print(f"[collect_target_info] Wrote all info to {output_file}")


def collect_config_files_target(packages_dir, source_config_list):
    """
    对于源系统关注的配置文件(如 /etc/fstab, /etc/ssh/sshd_config 等)，
    在 ISO Packages 中用 rpm -qpl 查有没有对应路径.
    只返回 'exists: True/False' + 'found_in_rpms'
    """
    results = []
    for conf_path in source_config_list:
        if os.path.isdir(conf_path):
            # 如果是目录，则展开其中文件
            file_list = []
            for root, dirs, files in os.walk(conf_path):
                for fname in files:
                    file_list.append(os.path.join(root, fname))
            # flatten
            for p in file_list:
                results.append(check_config_in_rpms(p, packages_dir))
        else:
            results.append( check_config_in_rpms(conf_path, packages_dir) )
    return results


def check_config_in_rpms(conf_path, packages_dir):
    # 先处理 conf_full
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

    # ★ 在这里加一个小提示，告诉用户总共有多少 rpm
    print(f"[check_config_in_rpms] Checking {conf_path} in {total_rpms} RPMs...")

    for i, rpm_name in enumerate(rpms, start=1):
        # ★ 打印当前进度
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
    """
    简化：收集 .ko 文件 => 说明可用哪些内核模块
    """
    data = {
        "kernel_modules": []
    }
    modules_set = set()
    rpms = [f for f in os.listdir(packages_dir) if f.endswith(".rpm")]
    total_rpms = len(rpms)

    # ★ 打印提示
    print(f"[collect_hardware_info_target] Found {total_rpms} RPMs. Checking for .ko files...")

    for i, rpm_name in enumerate(rpms, start=1):
        # ★ 显示进度
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
    """
    检查常见命令( /bin/<cmd> /usr/bin/<cmd> /usr/sbin/<cmd> ) 是否有
    """
    # 可能路径
    possible_paths = []
    for c in COMMON_COMMANDS:
        possible_paths.append(f"/bin/{c}")
        possible_paths.append(f"/usr/bin/{c}")
        possible_paths.append(f"/usr/sbin/{c}")
        possible_paths.append(f"/usr/local/bin/{c}")

    cmd_map = {c:{"name":c,"exists":False,"found_in_rpms":[]} for c in COMMON_COMMANDS}

    rpms = [f for f in os.listdir(packages_dir) if f.endswith(".rpm")]
    total_rpms = len(rpms)

    # ★ 打印提示
    print(f"[collect_commands_target] Found {total_rpms} RPMs. Checking commands...")

    for i, rpm_name in enumerate(rpms, start=1):
        # ★ 显示进度
        print(f"  -> ({i}/{total_rpms}) Checking {rpm_name}")
        rpm_path = os.path.join(packages_dir, rpm_name)
        try:
            res = subprocess.run(["rpm","--nosignature","-qpl",rpm_path],
                                 stdout=subprocess.PIPE, text=True)
            file_list = res.stdout.strip().split("\n")
            for c in COMMON_COMMANDS:
                if not cmd_map[c]["exists"]:
                    for p in possible_paths:
                        if p.endswith(f"/{c}") and (p in file_list):
                            cmd_map[c]["exists"] = True
                            cmd_map[c]["found_in_rpms"].append(rpm_name)
        except:
            pass

    return list(cmd_map.values())



########################################
# 4. 差异分析（把三个方面合并对比）
########################################

def compare_all(source_json="source_all.json", target_json="target_all.json", diff_json="all_diff.json"):
    """
    对比“source_all.json”和“target_all.json”里:
    1. config_files
    2. hardware_info
    3. commands
    并把结果输出到 all_diff.json
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


#### 4.1 配置文件对比
def compare_config_section(src_config, tgt_config):
    """
    src_config: list of {file_path, exists, is_directory, content_lines, mode, mtime, size}
    tgt_config: list of {file_path, exists, found_in_rpms} (仅静态信息)
    """
    # 先把source用 path做索引
    src_map = { item["file_path"] : item for item in src_config }
    diff = {
        "missing_in_target": [],
        "found_in_target": [],
        "content_note": "Target only provides file path existence (no actual content)."
    }

    # target 是( path -> {exists, found_in_rpms} ), 但我们这儿把它list化了
    # 需要做同样的map
    tgt_map = { item["file_path"] : item for item in tgt_config }

    for spath, sitem in src_map.items():
        # 若源系统不存在，也无需对比
        if not sitem["exists"]:
            continue
        # 看目标
        titem = tgt_map.get(spath)
        if titem is None:
            # 目标系统没有记录
            diff["missing_in_target"].append(spath)
        else:
            if not titem["exists"]:
                diff["missing_in_target"].append(spath)
            else:
                # 目标存在 => 记录 found_in_target
                diff["found_in_target"].append({
                    "file_path": spath,
                    "found_in_rpms": titem["found_in_rpms"]
                })
    return diff

#### 4.2 硬件与驱动对比
def compare_hardware_section(src_hw, tgt_hw):
    """
    src_hw = {"pci_devices": [...], "usb_devices": [...], "loaded_modules": [...]}
    tgt_hw = {"kernel_modules": [...]}
    仅对比 loaded_modules vs kernel_modules (PCI/USB 无法真正对比).
    """
    diff = {
        "missing_modules_in_target": [],
        "extra_modules_in_target": []
    }
    src_mods = set(src_hw.get("loaded_modules",[]))
    tgt_mods = set(tgt_hw.get("kernel_modules",[]))
    diff["missing_modules_in_target"] = list(src_mods - tgt_mods)
    diff["extra_modules_in_target"] = list(tgt_mods - src_mods)
    return diff

#### 4.3 命令对比
def compare_command_section(src_cmds, tgt_cmds):
    """
    src_cmds: list of {name, exists, which_path, version_info}
    tgt_cmds: list of {name, exists, found_in_rpms}
    """
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
                # 都存在 => 记录
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
    """
    用法示例:
    1) python collect_and_compare_all.py source
       -> 在CentOS源系统上采集, 生成 source_all.json

    2) python collect_and_compare_all.py target
       -> 对挂载在 /mnt/iso 上的openEuler ISO做静态分析, 生成 target_all.json

    3) python collect_and_compare_all.py compare
       -> 对 source_all.json 和 target_all.json 做汇总对比, 生成 all_diff.json
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python collect_and_compare_all.py source [output_file]")
        print("  python collect_and_compare_all.py target [output_file]")
        print("  python collect_and_compare_all.py compare [source_json] [target_json] [diff_json]")
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
