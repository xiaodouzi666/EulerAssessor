import json

def analyze_package_differences(source_file, target_file, output_file="package_differences.json"):
    """
    Compare two JSON files containing software package information and identify:
    - Added packages
    - Removed packages
    - Updated package versions
    - Dependency changes
    - File differences
    """
    try:
        with open(source_file, "r", encoding="utf-8") as src_file:
            source_data = json.load(src_file)
        
        with open(target_file, "r", encoding="utf-8") as tgt_file:
            target_data = json.load(tgt_file)

        source_packages = {pkg["name"].lower(): pkg for pkg in source_data.get("software_packages", [])}
        target_packages = {pkg["name"].lower(): pkg for pkg in target_data.get("software_packages", [])}

        # 1. 新增包
        added_packages = {
            pkg_name: target_packages[pkg_name]
            for pkg_name in target_packages if pkg_name not in source_packages
        }
        # 2. 删除包
        removed_packages = {
            pkg_name: source_packages[pkg_name]
            for pkg_name in source_packages if pkg_name not in target_packages
        }
        # 3. 更新包
        updated_packages = {
            pkg_name: {
                "old_version": source_packages[pkg_name]["version"],
                "new_version": target_packages[pkg_name]["version"]
            }
            for pkg_name in source_packages 
            if pkg_name in target_packages and source_packages[pkg_name]["version"] != target_packages[pkg_name]["version"]
        }
        # 4. 依赖变更
        dependency_differences = {
            pkg_name: {
                "removed_dependencies": list(set(source_packages[pkg_name].get("dependencies", [])) - set(target_packages[pkg_name].get("dependencies", []))),
                "added_dependencies": list(set(target_packages[pkg_name].get("dependencies", [])) - set(source_packages[pkg_name].get("dependencies", [])))
            }
            for pkg_name in source_packages 
            if pkg_name in target_packages and set(source_packages[pkg_name].get("dependencies", [])) != set(target_packages[pkg_name].get("dependencies", []))
        }
        # 5. 文件变更
        file_differences = {
            pkg_name: {
                "removed_files": list(set(source_packages[pkg_name].get("files", [])) - set(target_packages[pkg_name].get("files", []))),
                "added_files": list(set(target_packages[pkg_name].get("files", [])) - set(source_packages[pkg_name].get("files", [])))
            }
            for pkg_name in source_packages 
            if pkg_name in target_packages and set(source_packages[pkg_name].get("files", [])) != set(target_packages[pkg_name].get("files", []))
        }

        # 合并结果
        package_differences = {
            "added_packages": added_packages,
            "removed_packages": removed_packages,
            "updated_packages": updated_packages,
            "dependency_differences": dependency_differences,
            "file_differences": file_differences
        }

        # 写入 package_differences.json
        with open(output_file, "w", encoding="utf-8") as out_file:
            json.dump(package_differences, out_file, indent=4, ensure_ascii=False)
        
        print(f"Package differences analyzed and saved to {output_file}.")

    except Exception as e:
        print(f"Error during package difference analysis: {e}")

if __name__ == "__main__":
    analyze_package_differences("sourceinfo.json", "targetinfo.json")
