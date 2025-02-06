import json
import platform
import subprocess


def collect_packages(output_file="system_packages.json"):
    """
    Collect installed software packages from the system and save to a JSON file.
    :param output_file: Path to the output JSON file for collected data.
    """
    packages = []

    if platform.system() == "Linux":
        # Collect packages using rpm command
        try:
            result = subprocess.getoutput("rpm -qa")
            for line in result.split("\n"):
                if line:
                    name, version = line.split("-")[:2]
                    packages.append({"name": name, "version": version})
        except Exception as e:
            print(f"Error collecting Linux packages: {e}")

    elif platform.system() == "Windows":
        # Collect packages using wmic command
        try:
            result = subprocess.getoutput("wmic product get name,version")
            for line in result.split("\n")[1:]:  # Skip header row
                parts = line.split()
                if len(parts) >= 2:
                    name = " ".join(parts[:-1])
                    version = parts[-1]
                    packages.append({"name": name, "version": version})
        except Exception as e:
            print(f"Error collecting Windows packages: {e}")

    # Save collected packages to JSON
    with open(output_file, "w") as out_file:
        json.dump({"software_packages": packages}, out_file, indent=4)

    print(f"Packages collected and saved to {output_file}.")


def analyze_package_differences(source_file, target_file, output_file="package_differences.json"):
    """
    Analyze differences in software packages between two system states.
    :param source_file: Path to the source system JSON file.
    :param target_file: Path to the target system JSON file.
    :param output_file: Path to the output JSON file for differences.
    """
    try:
        # Load source and target system data
        with open(source_file, "r") as src_file:
            source_data = json.load(src_file)
        
        with open(target_file, "r") as tgt_file:
            target_data = json.load(tgt_file)

        # Extract software package lists
        source_packages = {pkg["name"]: pkg["version"] for pkg in source_data.get("software_packages", [])}
        target_packages = {pkg["name"]: pkg["version"] for pkg in target_data.get("software_packages", [])}

        # Compare packages
        added_packages = [pkg for pkg in target_packages if pkg not in source_packages]
        removed_packages = [pkg for pkg in source_packages if pkg not in target_packages]
        updated_packages = {
            pkg: {"old_version": source_packages[pkg], "new_version": target_packages[pkg]}
            for pkg in source_packages if pkg in target_packages and source_packages[pkg] != target_packages[pkg]
        }

        # Prepare result
        package_differences = {
            "added": added_packages,
            "removed": removed_packages,
            "updated": updated_packages
        }

        # Save result to output file
        with open(output_file, "w") as out_file:
            json.dump(package_differences, out_file, indent=4)
        
        return f"Package differences analyzed and saved to {output_file}."
    
    except Exception as e:
        return f"Error during package difference analysis: {e}"


if __name__ == "__main__":
    # Example: Collect packages from two systems (source and target)
    collect_packages(output_file="source_system.json")
    collect_packages(output_file="target_system.json")
    
    # Example: Analyze differences between the two collected states
    result_message = analyze_package_differences("source_system.json", "target_system.json")
    print(result_message)
