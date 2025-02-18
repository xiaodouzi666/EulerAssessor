#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import platform
import subprocess
import re
import shutil
from datetime import datetime
import tempfile

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
# 这里演示 python3.9, 你也可以改回 python3
COMMON_COMMANDS = ["bash","sh","python3.9","gcc","docker","git","java","systemctl"]


########################################
# 2. 采集逻辑 -- 源系统
########################################

def collect_source_info(output_file="source_all.json"):
    data = {}
    # 配置文件
    data["config_files"] = collect_config_files(SOURCE_CONFIG_FILES)
    # 硬件驱动
    data["hardware_info"] = collect_hardware_info_source()
    # 命令可用性
    data["commands"] = collect_commands_source()
    # OS信息
    data["os_info"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture()[0]
    }
    # 额外
    if platform.system() == "Linux":
        data["network_info"] = subprocess.getoutput("ss -tuln")
        data["services_info"] = subprocess.getoutput("systemctl list-units --type=service --state=running")
        data["processes"] = subprocess.getoutput("ps -aux")
        data["disk_info"] = subprocess.getoutput("lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT")
        data["environment_variables"] = dict(os.environ)
    else:
        data["network_info"] = "N/A"
        data["services_info"] = "N/A"
        data["processes"] = "N/A"
        data["disk_info"] = "N/A"
        data["environment_variables"] = {}

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
            res = subprocess.run(["which", cmd],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
            if res.returncode == 0:
                info["exists"] = True
                info["which_path"] = res.stdout.strip()
                ver_res = subprocess.run([cmd, "--version"],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
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
    data = {}
    # 1) 先用旧逻辑: rpm -qpl => config_files
    data["config_files"] = collect_config_files_target(iso_packages_dir, SOURCE_CONFIG_FILES)
    # 2) 硬件驱动 => .ko (带modinfo)
    data["hardware_info"] = collect_hardware_info_target(iso_packages_dir)
    # 3) 命令可用性
    data["commands"] = collect_commands_target(iso_packages_dir)
    # 4) OS信息(占位)
    data["os_info"] = {
        "system": "openEuler",
        "release": "24.03-LTS-SP1",
        "version": "unknown",
        "architecture": "x86_64"
    }
    # 5) 占位: network,services,processes,disk,env
    data["network_info"] = "tcp LISTEN 0 128 0.0.0.0:22 ...\ntcp LISTEN 0 128 :::22 ..."
    data["services_info"] = "UNIT                     LOAD   ACTIVE SUB     DESCRIPTION\nsshd.service             loaded active running OpenSSH server daemon"
    data["processes"] = "root       1  0.0  0.1  19344  1612 ?  Ss   00:00:01 /usr/lib/systemd/systemd\n..."
    data["disk_info"] = "NAME  FSTYPE  SIZE MOUNTPOINT\nsda   xfs     60G  /\nsr0   iso9660 4.3G /mnt/iso"
    data["environment_variables"] = {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin",
        "HOME": "/root",
        "LANG": "en_US.UTF-8"
    }

    # 6) 解包配置文件
    for item in data["config_files"]:
        if item.get("exists"):
            file_path = item["file_path"]
            rpmlist = item.get("found_in_rpms", [])
            if rpmlist:
                rpm_name = rpmlist[0]
                rpm_fullpath = os.path.join(iso_packages_dir, rpm_name)
                file_content_info = extract_file_from_rpm(rpm_fullpath, file_path)
                if file_content_info is not None:
                    item["content_lines"] = file_content_info["content_lines"]
                    item["mode"] = file_content_info["mode"]
                    item["size"] = file_content_info["size"]

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
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
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
    改动点:
      不再仅保存 .ko 文件名列表,
      而是对每个 RPM 解包 + 查找 .ko -> 对每个 ko 调 modinfo
      最终 kernel_modules 是 [ { name, version, license, ... }, ... ]
    """
    data = {}
    data["kernel_modules"] = []

    rpms = [f for f in os.listdir(packages_dir) if f.endswith(".rpm")]
    total_rpms = len(rpms)
    print(f"[collect_hardware_info_target] Found {total_rpms} RPMs. Checking .ko modinfo...")

    for i, rpm_name in enumerate(rpms, start=1):
        rpm_path = os.path.join(packages_dir, rpm_name)
        print(f"  -> ({i}/{total_rpms}) Analyzing {rpm_name}")
        ko_list = extract_all_kos_and_modinfo(rpm_path)
        data["kernel_modules"].extend(ko_list)

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
                                 stdout=subprocess.PIPE, universal_newlines=True)
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
# --------------解包/解析函数------------------
########################################

def extract_file_from_rpm(rpm_path, file_path):
    """
    用 rpm2cpio + cpio 解包 rpm_path 到临时目录，看看能否找到 file_path
    若找到，就读取其内容+权限等，返回: {
      "content_lines": [...],
      "mode": "0o644",
      "size": 123
    }
    如果找不到，或发生异常，返回 None
    """
    tmp_dir = tempfile.mkdtemp(prefix="rpmextract_")
    try:
        cmd = f"rpm2cpio '{rpm_path}' | cpio -idmv"
        res = subprocess.run(cmd, shell=True, cwd=tmp_dir,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)

        if res.returncode != 0:
            print(f"extract_file_from_rpm: cpio failed: {res.stderr}")
            return None

        rel_path = file_path.lstrip("/")
        actual_path = os.path.join(tmp_dir, rel_path)

        if not os.path.exists(actual_path):
            print(f"extract_file_from_rpm: {file_path} not found in {rpm_path}")
            return None

        info = {
            "content_lines": [],
            "mode": None,
            "size": None
        }
        try:
            st = os.stat(actual_path)
            info["mode"] = oct(st.st_mode & 0o777)
            info["size"] = st.st_size

            if os.path.isfile(actual_path):
                with open(actual_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                info["content_lines"] = [ln.rstrip("\n") for ln in lines]
            else:
                info["content_lines"] = ["[Directory extracted]"]
        except Exception as e:
            info["content_lines"] = [f"[Error reading: {e}]"]

        return info
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def extract_all_kos_and_modinfo(rpm_path):
    """
    解包 rpm_path, 找所有 .ko
    对每个 .ko 调 modinfo, 组装成 {name, version, license, ...}
    返回list
    """
    ko_list = []
    tmp_dir = tempfile.mkdtemp(prefix="rpm_kos_")
    try:
        cmd = f"rpm2cpio '{rpm_path}' | cpio -idmv"
        res = subprocess.run(cmd, shell=True, cwd=tmp_dir,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)

        if res.returncode != 0:
            print(f"[extract_all_kos_and_modinfo] cpio failed for {rpm_path}: {res.stderr}")
            return ko_list

        for root, dirs, files in os.walk(tmp_dir):
            for fname in files:
                if fname.endswith(".ko"):
                    full_ko_path = os.path.join(root, fname)
                    modinfo_data = run_modinfo_on_ko(full_ko_path)
                    # name => fname
                    item = {"name": fname}
                    # 把常见字段写进去
                    if modinfo_data:
                        if "version" in modinfo_data:
                            item["version"] = modinfo_data["version"]
                        if "license" in modinfo_data:
                            item["license"] = modinfo_data["license"]
                        if "author" in modinfo_data:
                            item["author"] = modinfo_data["author"]
                        if "description" in modinfo_data:
                            item["description"] = modinfo_data["description"]
                        if "depends" in modinfo_data:
                            item["depends"] = modinfo_data["depends"]
                    ko_list.append(item)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return ko_list


def run_modinfo_on_ko(ko_path):
    """
    调用 modinfo <ko_path>, 返回解析后的字典:
      { 'filename':..., 'version':..., 'license':..., 'description':..., 'author':..., 'depends':... }
    """
    res_dict = {}
    try:
        mod_res = subprocess.run(["modinfo", ko_path],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        if mod_res.returncode == 0:
            for ln in mod_res.stdout.split("\n"):
                ln = ln.strip()
                if not ln:
                    continue
                if ":" in ln:
                    key, val = ln.split(":", 1)
                    key = key.strip().lower()      # modinfo里是 version: xxx
                    val = val.strip()
                    res_dict[key] = val
    except Exception as e:
        print(f"run_modinfo_on_ko: exception {e}")
    return res_dict


########################################
# 4. 差异分析 => all_diff.json
########################################

def compare_all(source_json="source_all.json", target_json="target_all.json", diff_json="all_diff.json"):
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
        "content_note": "Target might have real content if we used rpm2cpio."
    }
    tgt_map = { item["file_path"] : item for item in tgt_config }

    for spath, sitem in src_map.items():
        if not sitem["exists"]:
            continue
        titem = tgt_map.get(spath)
        if titem is None:
            diff["missing_in_target"].append(spath)
        else:
            if not titem.get("exists", False):
                diff["missing_in_target"].append(spath)
            else:
                diff["found_in_target"].append({
                    "file_path": spath,
                    "found_in_rpms": titem.get("found_in_rpms", []),
                })
    return diff


def compare_hardware_section(src_hw, tgt_hw):
    diff = {
        "missing_modules_in_target": [],
        "extra_modules_in_target": []
    }
    # 源侧 loaded_modules vs 目标侧 kernel_modules (后者是详细对象,
    #  但我们只比 "name" 字段 或把老的是字符串? 这里做简单set对比
    src_mods = set(src_hw.get("loaded_modules",[]))

    # 目标现在是 [ { name: "xxx.ko", version:..., ...}, ...]
    # 先拿名称做set
    tgt_mod_list = tgt_hw.get("kernel_modules", [])
    tgt_names = set(obj["name"] for obj in tgt_mod_list)

    diff["missing_modules_in_target"] = list(src_mods - tgt_names)
    diff["extra_modules_in_target"] = list(tgt_names - src_mods)
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
