# server.py
from flask import Flask, jsonify, request
import subprocess
import os
import json

app = Flask(__name__)

##################################
# 1. 环境兼容信息收集 (侧边栏1)
##################################

@app.route("/api/collect/source", methods=["POST"])
def collect_source():
    """
    触发对源系统的信息收集。
    生成 source_all.json (由 collect_and_compare_all.py source 完成)
    """
    try:
        res = subprocess.run(["python3", "collect_and_compare_all.py", "source"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            return jsonify({
                "message": "Source system info collected successfully.",
                "output_file": "source_all.json",
                "stdout": res.stdout
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
    触发对目标系统(ISO)的信息收集。
    生成 target_all.json (由 collect_and_compare_all.py target 完成)
    """
    try:
        res = subprocess.run(["python3", "collect_and_compare_all.py", "target"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            return jsonify({
                "message": "Target system info collected successfully.",
                "output_file": "target_all.json",
                "stdout": res.stdout
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
    调用 difference.py 分析软件包差异 (sourceinfo.json vs. targetinfo.json)，
    生成 package_differences.json
    """
    try:
        cmd = [
            "python3", "difference.py",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return jsonify({
                "message": "Package differences analyzed",
                "output_file": "package_differences.json",
                "stdout": res.stdout
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
    返回 package_differences.json 的内容给前端，
    用于展示软件包差异: added, removed, updated, dependencies, file diff 等
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
    触发 collect_and_compare_all.py compare
    用 source_all.json + target_all.json 做对比, 生成 all_diff.json
    其中包括:
      config_diff, hardware_diff, command_diff
    """
    try:
        res = subprocess.run(["python3", "collect_and_compare_all.py", "compare"],
                             capture_output=True, text=True)
        if res.returncode == 0:
            return jsonify({
                "message": "Compare done",
                "output_file": "all_diff.json",
                "stdout": res.stdout
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
      config_diff -> (配置文件对比)
      hardware_diff -> (硬件兼容/驱动对比)
      command_diff -> (命令可用性对比)
    前端在侧边栏3,4,5分别解析并展示
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
# (6) 迁移可行性评估建议 => 还没搞完，先空着
##########################################
# @app.route("/api/migration_assessment", methods=["GET","POST"])
# def migration_assessment():
# pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
