from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

########################
# 1. Mock 数据
########################

# 1.1 sourceinfo.json
MOCK_SOURCEINFO = {
    "software_packages": [
        {
            "name": "device-mapper",
            "version": "1.02.170-6.el7_9.5",
            "dependencies": ["/bin/bash","/bin/sh","device-mapper-libs = 7:1.02.170-6.el7_9.5","libc.so.6()(64bit)"],
            "files": [
                "/usr/lib/systemd/system/blk-availability.service",
                "/usr/sbin/dmsetup",
                "/usr/share/doc/device-mapper-1.02.170/COPYING"
            ]
        }
    ]
}

# 1.2 targetinfo.json
MOCK_TARGETINFO = {
    "software_packages": [
        {
            "name": "abattis-cantarell-fonts",
            "version": "0.303.1",
            "dependencies": ["fontpackages-filesystem","rpmlib(CompressedFileNames) <= 3.0.4-1"],
            "files": [
                "/etc/fonts/conf.d/31-cantarell.conf",
                "/usr/share/fonts/abattis-cantarell-fonts/Cantarell-VF.otf"
            ]
        }
    ]
}

# 1.3 package_differences.json
MOCK_PACKAGE_DIFF = {
    "added_packages": {
        "my-new-package": {
            "name": "my-new-package",
            "version": "2.0.1",
            "dependencies": ["libxxx.so.1()(64bit)"],
            "files": ["/usr/bin/my-new-cmd"]
        }
    },
    "removed_packages": {
        "old-package": {
            "name": "old-package",
            "version": "1.0"
        }
    },
    "updated_packages": {
        "gcc": {
            "old_version": "4.8.5",
            "new_version": "12.3.1"
        }
    },
    "dependency_differences": {
        "bash": {
            "removed_dependencies": ["libabc.so"],
            "added_dependencies": ["libxyz.so"]
        }
    },
    "file_differences": {
        "git": {
            "removed_files": ["/usr/share/doc/oldstuff"],
            "added_files": ["/usr/share/doc/newstuff"]
        }
    }
}

# 1.4 source_all.json —— 合并“网络状态+端口”为 network_info
MOCK_SOURCE_ALL = {
    "config_files": [
        {
            "file_path": "/etc/fstab",
            "exists": True,
            "is_directory": False,
            "content_lines": [
                "# /etc/fstab mock content ...",
                "/dev/mapper/centos-root / xfs defaults 0 0"
            ],
            "mode": "0o644",
            "mtime": "2024-11-29T00:50:56.205000",
            "size": 465
        },
        {
            "file_path": "/etc/ssh/sshd_config",
            "exists": True,
            "is_directory": False,
            "content_lines": [
                "[Error reading: [Errno 13] Permission denied: '/etc/ssh/sshd_config']"
            ],
            "mode": "0o600",
            "mtime": "2023-08-05T00:00:49",
            "size": 3907
        }
    ],
    "hardware_info": {
        "pci_devices": [
            {"bus_id": "00:03.0", "description": "VGA compatible controller"}
        ],
        "usb_devices": [
            "Bus 001 Device 002: ID 0e0f:0003 VMware"
        ],
        "loaded_modules": [
            "dm_mod","sd_mod","sr_mod"
        ]
    },
    "commands": [
        {
            "name": "bash",
            "exists": True,
            "which_path": "/usr/bin/bash",
            "version_info": "GNU bash, version 4.2.46(2)-release"
        },
        {
            "name": "java",
            "exists": False
        }
    ],
    "os_info": {
        "system": "Linux",
        "release": "3.10.0-957.el7.x86_64",
        "version": "#1 SMP Thu Nov 29 ...",
        "architecture": "x86_64"
    },
    "network_info": "tcp LISTEN 0 128 0.0.0.0:22 ...\ntcp LISTEN 0 128 :::22 ...",
    "services_info": "UNIT                            LOAD   ACTIVE SUB     DESCRIPTION\nsshd.service                    loaded active running OpenSSH server daemon",
    "processes": "root       1  0.0  0.1  19344  1612 ?  Ss   00:00:01 /usr/lib/systemd/systemd\nroot     123  0.2  0.5  54768  3000 ?  S    00:05:33 /usr/bin/python\n",
    "disk_info": "NAME  FSTYPE  SIZE MOUNTPOINT\nsda   xfs     40G  /\nsr0   iso9660 4.3G /mnt/cdrom",
    "environment_variables": {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin",
        "HOME": "/root",
        "LANG": "en_US.UTF-8"
    }
}

# 1.5 target_all.json —— 把网络状态和端口合并放 network_info
MOCK_TARGET_ALL = {
    "config_files": [
        {
            "file_path": "/etc/fstab",
            "exists": True,
            "found_in_rpms": [
                "setup-2.14.5-2.oe2403sp1.noarch.rpm"
            ]
        },
        {
            "file_path": "/etc/ssh/sshd_config",
            "exists": True,
            "found_in_rpms": [
                "openssh-server-9.6p1-3.oe2403sp1.x86_64.rpm"
            ]
        },
        {
            "file_path": "/etc/sysctl.conf",
            "exists": True,
            "found_in_rpms": [
                "systemd-255-34.oe2403sp1.x86_64.rpm"
            ]
        }
    ],
    "hardware_info": {
        "kernel_modules": [
            "igb_uio.ko",
            "smc_acc.ko"
        ]
    },
    "commands": [
        {
            "name": "bash",
            "exists": True,
            "found_in_rpms": [
                "bash-5.2.15-14.oe2403sp1.x86_64.rpm"
            ]
        },
        {
            "name": "java",
            "exists": False
        }
    ],
    "os_info": {
        "system": "openEuler",
        "release": "24.03-LTS-SP1",
        "version": "unknown",
        "architecture": "x86_64"
    },
    "network_info": "tcp LISTEN 0 128 0.0.0.0:22 ...\ntcp LISTEN 0 128 :::22 ...",
    "services_info": "UNIT                     LOAD   ACTIVE SUB     DESCRIPTION\nsshd.service             loaded active running OpenSSH server daemon",
    "processes": "root       1  0.0  0.1  19344  1612 ?  Ss   00:00:01 /usr/lib/systemd/systemd\nroot     222  0.2  0.5  54768  3000 ?  S    00:05:33 /usr/bin/python\n",
    "disk_info": "NAME  FSTYPE  SIZE MOUNTPOINT\nsda   xfs     60G  /\nsr0   iso9660 4.3G /mnt/iso",
    "environment_variables": {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin",
        "HOME": "/root",
        "LANG": "en_US.UTF-8"
    }
}

# 1.6 all_diff.json (保持不变)
MOCK_ALL_DIFF = {
    "config_diff": {
        "missing_in_target": [
            "/etc/yum.repos.d/CentOS-CR.repo",
            "/etc/yum.repos.d/CentOS-Debuginfo.repo"
        ],
        "found_in_target": [
            {
                "file_path": "/etc/fstab",
                "found_in_rpms": [
                    "setup-2.14.5-2.oe2403sp1.noarch.rpm"
                ]
            }
        ],
        "content_note": "Target only provides file path existence (no actual content)."
    },
    "hardware_diff": {
        "missing_modules_in_target": [
            "dm_log","i2c_piix4","libata"
        ],
        "extra_modules_in_target": [
            "igb_uio.ko","smc_acc.ko"
        ]
    },
    "command_diff": {
        "missing_in_target": ["java"],
        "found_in_target": [
            {
                "name": "bash",
                "source_version": "GNU bash, version 4.2.46(2)-release",
                "found_in_rpms": [
                    "bash-5.2.15-14.oe2403sp1.x86_64.rpm"
                ]
            }
        ],
        "version_info_note": "Target side no real version (just presence)."
    }
}


########################
# 2. Mock 接口
########################

@app.route("/api/sourceinfo", methods=["GET"])
def get_sourceinfo():
    return jsonify(MOCK_SOURCEINFO), 200

@app.route("/api/targetinfo", methods=["GET"])
def get_targetinfo():
    return jsonify(MOCK_TARGETINFO), 200

@app.route("/api/packages/differences", methods=["GET"])
def packages_diff_result():
    return jsonify(MOCK_PACKAGE_DIFF), 200

@app.route("/api/sourceall", methods=["GET"])
def get_source_all():
    return jsonify(MOCK_SOURCE_ALL), 200

@app.route("/api/targetall", methods=["GET"])
def get_target_all():
    return jsonify(MOCK_TARGET_ALL), 200

@app.route("/api/diffresult", methods=["GET"])
def get_diff_result():
    return jsonify(MOCK_ALL_DIFF), 200


# 在data字段里带对应mock数据
@app.route("/api/collect/source", methods=["POST"])
def collect_source():
    return jsonify({
        "message": "Source system info collected successfully (mock).",
        "output_file": "source_all.json",
        "stdout": "Pretend script output for source...",
        "data": MOCK_SOURCE_ALL
    }), 200

@app.route("/api/collect/target", methods=["POST"])
def collect_target():
    return jsonify({
        "message": "Target system info collected successfully (mock).",
        "output_file": "target_all.json",
        "stdout": "Pretend script output: all done.",
        "data": MOCK_TARGET_ALL
    }), 200

@app.route("/api/packages/compare", methods=["POST"])
def packages_compare():
    return jsonify({
        "message": "Package differences analyzed (mock).",
        "output_file": "package_differences.json",
        "stdout": "Pretend difference analysis logs...",
        "data": MOCK_PACKAGE_DIFF
    }), 200

@app.route("/api/compare", methods=["POST"])
def compare_source_target():
    return jsonify({
        "message": "Compare done (mock).",
        "output_file": "all_diff.json",
        "stdout": "Pretend compare logs...",
        "data": MOCK_ALL_DIFF
    }), 200

########################
# 3. 新增了一个讨论后的针对前端页面的接口
########################
@app.route("/api/mock_diff_data", methods=["GET"])
def mock_diff_data():
    """
    一次性返回:
      1) oldJson 和 newJson: 用于 JSON 对比(配置文件对比等)
      2) compatibility: 用于兼容性分析列表(如 动态库接口/动态API 的 oldVer/newVer)
      3) packages_table: 用于软件包分析(展示成表格)
    """
    oldJson = {
        "description": "Product Driver (old)",
        "keywords": ["electron", "react", "webpack", "typescript"],
        "license": "MIT",
        "main": "./src/main/main.ts",
        "scripts": {
            "build": "concurrently \"npm run build:main\" \"npm run build:renderer\"",
            "start": "electron ."
        }
    }

    newJson = {
        "description": "Product Driver (new)",
        "keywords": ["electron", "react", "sass", "hot-reload"],
        "main": "./src/main/main.ts",
        "scripts": {
            "build": "concurrently \"npm run build:all\"",
            "start": "electron .",
            "test": "jest"
        }
    }

    # 兼容性分析示例: oldVer/newVer 表示是否在旧版/新版中存在
    compatibility = [
        {"label": "动态库接口1", "oldVer": False, "newVer": True},
        {"label": "动态库接口2", "oldVer": True,  "newVer": True},
        {"label": "动态库接口3", "oldVer": True,  "newVer": False},
        {"label": "动态库接口4", "oldVer": False, "newVer": False}  # 仅示例
    ]

    # 软件包分析: 每项代表一行，可根据前端需求扩展更多字段
    packages_table = [
        {
            "key": 1,
            "name": "device-mapper",
            "version": "1.02.170-6.el7_9.5",
            "tags": ["system", "core"],
            "action": "Install/Remove"
        },
        {
            "key": 2,
            "name": "bash",
            "version": "4.2.46(2)-release",
            "tags": ["shell"],
            "action": "Install/Remove"
        },
        {
            "key": 3,
            "name": "gcc",
            "version": "4.8.5",
            "tags": ["compiler"],
            "action": "Install/Remove"
        }
    ]

    data = {
        "oldJson": oldJson,
        "newJson": newJson,
        "compatibility": compatibility,
        "packages_table": packages_table
    }
    return jsonify(data), 200

########################
# 4. 新增迁移建议接口
########################

@app.route("/api/migration_assessment_mock", methods=["GET"])
def migration_assessment_mock():
    """
    Mock接口：根据对比信息，给出迁移可行性建议/风险/评分等。
    """
    assessment_data = {
        "score": 85,  # 可行性分数: 0~100
        "message": "系统迁移可行性较高，需关注以下风险项并做相应调整。",
        "risks": [
            {
                "id": 1,
                "title": "缺失的软件包 'java'",
                "description": "目标系统未包含Java运行环境，如有Java应用需手动安装。"
            },
            {
                "id": 2,
                "title": "某些内核模块缺失",
                "description": "dm_log, i2c_piix4 等模块在目标系统中不存在，可能影响存储/传感器功能。"
            }
        ],
        "suggestions": [
            "手动安装OpenJDK或将Java应用替换为兼容方案",
            "编译加载缺失的内核模块，或使用对应功能的替代驱动",
            "备份 /etc/yum.repos.d 配置，确保网络仓库正常"
        ]
    }
    return jsonify(assessment_data), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
