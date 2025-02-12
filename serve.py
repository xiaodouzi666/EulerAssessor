# serve.py
from flask import Flask, jsonify, request
import subprocess
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

##################################
# 1. 环境兼容信息收集 (侧边栏1)
##################################

@app.route("/api/collect/source", methods=["POST"])
def collect_source():
    """
    调用 collect_and_compare_all.py source
    生成 source_all.json

    返回:
      {
        "message": "Source system info collected successfully.",
        "output_file": "source_all.json",
        "stdout": "脚本执行的标准输出",
        "data": {...}  # 如果文件存在，则返回 JSON 内容
      }
      或:
      {
        "error": "Failed to collect source system info.",
        "stderr": "脚本执行的错误输出"
      }
    """
    try:
        res = subprocess.run(["python3.9", "collect_and_compare_all.py", "source"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            # 如果脚本执行成功，再读取生成的 source_all.json
            data_content = None
            if os.path.exists("source_all.json"):
                try:
                    with open("source_all.json", "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                except Exception as e:
                    data_content = {"error_reading_file": str(e)}
            return jsonify({
                "message": "Source system info collected successfully.",
                "output_file": "source_all.json",
                "stdout": res.stdout,
                "data": data_content
            }), 200
        else:
            return jsonify({
                "error": "Failed to collect source system info.",
                "stderr": res.stderr
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/collect/target", methods=["POST"])
def collect_target():
    """
    调用 collect_and_compare_all.py target
    生成 target_all.json

    返回:
      {
        "message": "Target system info collected successfully.",
        "output_file": "target_all.json",
        "stdout": "脚本执行的标准输出",
        "data": {...}
      }
      或:
      {
        "error": "Failed to collect target system info.",
        "stderr": "脚本执行的错误输出"
      }
    """
    try:
        res = subprocess.run(["python3.9", "collect_and_compare_all.py", "target"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            data_content = None
            if os.path.exists("target_all.json"):
                try:
                    with open("target_all.json", "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                except Exception as e:
                    data_content = {"error_reading_file": str(e)}
            return jsonify({
                "message": "Target system info collected successfully.",
                "output_file": "target_all.json",
                "stdout": res.stdout,
                "data": data_content
            }), 200
        else:
            return jsonify({
                "error": "Failed to collect target system info.",
                "stderr": res.stderr
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


##########################################
# 2. 软件包分析 (侧边栏2)
##########################################

@app.route("/api/packages/compare", methods=["POST"])
def packages_compare():
    """
    调用 difference.py 分析软件包差异 (sourceinfo.json vs. targetinfo.json)
    生成 package_differences.json

    返回:
      {
        "message": "Package differences analyzed",
        "output_file": "package_differences.json",
        "stdout": "脚本执行的标准输出",
        "data": {...}
      }
      或:
      {
        "error": "Failed to analyze package differences",
        "stderr": "脚本执行的错误输出"
      }
    """
    try:
        cmd = ["python3.9", "difference.py"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            data_content = None
            if os.path.exists("package_differences.json"):
                try:
                    with open("package_differences.json", "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                except Exception as e:
                    data_content = {"error_reading_file": str(e)}
            return jsonify({
                "message": "Package differences analyzed",
                "output_file": "package_differences.json",
                "stdout": res.stdout,
                "data": data_content
            }), 200
        else:
            return jsonify({
                "error": "Failed to analyze package differences",
                "stderr": res.stderr
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/packages/differences", methods=["GET"])
def packages_diff_result():
    """
    返回 package_differences.json 的内容
    用于展示软件包差异: added, removed, updated, dependencies, file diff 等.
    """
    try:
        if not os.path.exists("package_differences.json"):
            return jsonify({"error":"package_differences.json not found"}), 404
        
        with open("package_differences.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


##########################################
# 3~5. 配置文件对比、硬件兼容、命令可用性 (侧边栏3,4,5)
##########################################

@app.route("/api/compare", methods=["POST"])
def compare_source_target():
    """
    调用 collect_and_compare_all.py compare
    用 source_all.json + target_all.json 做对比, 生成 all_diff.json
    包含:
      config_diff, hardware_diff, command_diff

    返回:
      {
        "message": "Compare done",
        "output_file": "all_diff.json",
        "stdout": "脚本执行日志",
        "data": {...}
      }
      或:
      {
        "error": "Compare command failed",
        "stderr": "脚本错误输出"
      }
    """
    try:
        res = subprocess.run(["python3.9", "collect_and_compare_all.py", "compare"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            data_content = None
            if os.path.exists("all_diff.json"):
                try:
                    with open("all_diff.json", "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                except Exception as e:
                    data_content = {"error_reading_file": str(e)}
            return jsonify({
                "message": "Compare done",
                "output_file": "all_diff.json",
                "stdout": res.stdout,
                "data": data_content
            }), 200
        else:
            return jsonify({
                "error": "Compare command failed",
                "stderr": res.stderr
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/diffresult", methods=["GET"])
def get_diff_result():
    """
    返回 all_diff.json 内容:
      config_diff -> 配置文件对比
      hardware_diff -> 硬件兼容/驱动对比
      command_diff -> 命令可用性对比
    """
    try:
        if not os.path.exists("all_diff.json"):
            return jsonify({"error":"all_diff.json not found"}), 404
        
        with open("all_diff.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


##########################################
# 新增接口: 直接返回各 JSON 文件内容
##########################################

@app.route("/api/sourceinfo", methods=["GET"])
def get_sourceinfo():
    """
    返回 sourceinfo.json 的内容:
    {
      "software_packages": [...]
    }
    """
    try:
        if not os.path.exists("sourceinfo.json"):
            return jsonify({"error": "sourceinfo.json not found"}), 404
        
        with open("sourceinfo.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/targetinfo", methods=["GET"])
def get_targetinfo():
    """
    返回 targetinfo.json 的内容:
    {
      "software_packages": [...]
    }
    """
    try:
        if not os.path.exists("targetinfo.json"):
            return jsonify({"error":"targetinfo.json not found"}), 404
        
        with open("targetinfo.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sourceall", methods=["GET"])
def get_source_all():
    """
    返回 source_all.json:
    {
      "config_files": [...],
      "hardware_info": {...},
      "commands": [...],
      "os_info": {...},
      "network_info": "...",
      "services_info": "...",
      "processes": "...",
      "disk_info": "...",
      "environment_variables": {...}
    }
    """
    try:
        if not os.path.exists("source_all.json"):
            return jsonify({"error":"source_all.json not found"}), 404
        
        with open("source_all.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/targetall", methods=["GET"])
def get_target_all():
    """
    返回 target_all.json:
    {
      "config_files": [...],
      "hardware_info": {...},
      "commands": [...],
      "os_info": {...},
      "network_info": "...",
      "services_info": "...",
      "processes": "...",
      "disk_info": "...",
      "environment_variables": {...}
    }
    """
    try:
        if not os.path.exists("target_all.json"):
            return jsonify({"error":"target_all.json not found"}), 404
        
        with open("target_all.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


##########################################
# (6) 迁移可行性评估建议 => 待完成
##########################################
# 在 /api/migration_assessment 接口中，补充关键库检查：
KEY_LIBRARIES = {
    "python3": {
        "score_penalty": 5,
        "title": "移除Python3",
        "description": "源系统含python3，但目标系统不包含，需要手动安装或更换语言环境",
        "suggestion": "在目标系统上安装python3或使用兼容版本"
    },
    "glibc": {
        "score_penalty": 8,
        "title": "移除glibc",
        "description": "glibc是GNU C库，许多应用依赖它，移除后系统核心功能或大部分程序无法正常运行",
        "suggestion": "请确保glibc版本正确安装，保持系统兼容"
    },
    "openssl": {
        "score_penalty": 5,
        "title": "移除OpenSSL",
        "description": "OpenSSL是常用加密库，缺失会导致SSH/HTTPS/加密相关功能不可用",
        "suggestion": "在目标系统上安装openssl或使用其兼容替代"
    },
    "systemd": {
        "score_penalty": 5,
        "title": "移除systemd",
        "description": "systemd是现代Linux主流的初始化系统和服务管理器，缺失会导致服务无法正常管理",
        "suggestion": "确保目标系统使用兼容的init系统或安装systemd"
    },
    # 如果你们还想加别的关键包，也可类似添加
}


@app.route("/api/migration_assessment", methods=["GET","POST"])
def migration_assessment():
    """
    根据 all_diff.json + package_differences.json 做简易的迁移可行性评估
    """
    all_diff_data = {}
    package_diff_data = {}

    # 1. 读取all_diff.json
    if os.path.exists("all_diff.json"):
        try:
            with open("all_diff.json", "r", encoding="utf-8") as f:
                all_diff_data = json.load(f)
        except Exception as e:
            return jsonify({"error": f"Error reading all_diff.json: {e}"}), 500

    # 2. 读取package_differences.json
    if os.path.exists("package_differences.json"):
        try:
            with open("package_differences.json", "r", encoding="utf-8") as f:
                package_diff_data = json.load(f)
        except Exception as e:
            return jsonify({"error": f"Error reading package_differences.json: {e}"}), 500

    score = 100
    risks = []
    suggestions = []

    # =========== 从 all_diff.json 中提取差异做打分 =============

    # 2.1 缺失命令
    cmd_diff = all_diff_data.get("command_diff", {})
    missing_cmds = cmd_diff.get("missing_in_target", [])
    for cmd in missing_cmds:
        if cmd == "java":
            score -= 5
            risks.append({
                "title": "缺失的软件包 'java'",
                "description": "目标系统未包含Java运行环境，如有Java应用需手动安装。"
            })
            suggestions.append("安装OpenJDK或替换为兼容语言运行环境")
        elif cmd in ["gcc", "git"]:
            score -= 3
            risks.append({
                "title": f"缺失的软件包 '{cmd}'",
                "description": f"目标系统未包含 {cmd}，可能影响编译或版本管理。"
            })
            suggestions.append(f"请安装 {cmd} 以保证正常使用")
        else:
            score -= 2
            risks.append({
                "title": f"缺失的命令 '{cmd}'",
                "description": f"目标系统未包含 {cmd} 命令"
            })
            suggestions.append(f"如需使用 {cmd}，请手动安装")

    # 2.2 缺失内核模块
    hw_diff = all_diff_data.get("hardware_diff", {})
    missing_mods = hw_diff.get("missing_modules_in_target", [])
    score -= 3 * len(missing_mods)  # 每个缺失模块扣3分
    if missing_mods:
        for mod in missing_mods:
            risks.append({
                "title": f"缺失的内核模块 '{mod}'",
                "description": "可能导致对应硬件或功能不可用"
            })
        suggestions.append("可选择手动编译或安装缺失的内核模块 (若需要)")

    # 2.3 缺失配置文件
    config_diff = all_diff_data.get("config_diff", {})
    missing_cfg = config_diff.get("missing_in_target", [])
    for cfile in missing_cfg:
        if "sshd_config" in cfile:
            score -= 5
            risks.append({
                "title": "缺失SSH配置文件",
                "description": f"目标系统未包含 {cfile}"
            })
            suggestions.append("请手动拷贝并合并/修改SSH配置")
        else:
            score -= 1
            risks.append({
                "title": f"缺失配置文件 '{cfile}'",
                "description": "目标系统未包含此配置文件"
            })

    # =========== 从 package_differences.json 中提取差异做打分 =============

    removed_pkgs = package_diff_data.get("removed_packages", {})

    # 3. 检查关键库
    for key_lib, info in KEY_LIBRARIES.items():
        if key_lib.lower() in removed_pkgs:  # 这里要考虑大小写
            score -= info["score_penalty"]
            risks.append({
                "title": info["title"],
                "description": info["description"]
            })
            suggestions.append(info["suggestion"])

    # 如果添加/删除包过多，也可以做简单提示
    added_pkgs = package_diff_data.get("added_packages", {})
    if len(added_pkgs) > 10:
        suggestions.append("目标系统新增包数量较多，请检查是否有多余安装")

    updated_pkgs = package_diff_data.get("updated_packages", {})
    if updated_pkgs:
        suggestions.append("部分软件包版本发生更新，请确认兼容性")

    # 4. 最终score和message
    if score < 0:
        score = 0
    if score >= 80:
        message = "系统迁移可行性较高"
    elif score >= 50:
        message = "系统迁移可行性一般，需要一定适配"
    else:
        message = "系统迁移风险较高，需要大量手动调整"

    # 整理风险列表时，为每条风险分配id
    final_risks = []
    for i, r in enumerate(risks, start=1):
        final_risks.append({
            "id": i,
            "title": r["title"],
            "description": r["description"]
        })

    assessment_data = {
        "score": score,
        "message": message,
        "risks": final_risks,
        "suggestions": suggestions
    }

    return jsonify(assessment_data), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
