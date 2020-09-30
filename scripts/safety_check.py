#!/usr/bin/env python
import argparse
import traceback
import json
import glob
import subprocess
import sys


IDS_TO_IGNORE = ['38197']


class Vulnerability(object):
    def __init__(self, package, affected_versions, message):
        self.package = package
        self.affected_versions = affected_versions
        self.message = message
        self.occurrences = []

    def with_occurrence(self, filename, version):
        self.occurrences.append({'filename': filename, 'version': version})
        return self


class SafetyCheck(object):
    def __init__(self, ids_to_ignore):
        self.ignored = {}
        self.failed = {}

        self.ids_to_ignore = set(ids_to_ignore)

    def to_json(self):
        return json.dumps(
            {'ignored': self.ignored, 'failed': self.failed},
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4,
        )

    def add(self, result, filename):
        package, affected_versions, curr_version, message, vulnerability_id = result
        if vulnerability_id in self.ids_to_ignore:
            if vulnerability_id in self.ignored:
                vuln = self.ignored[vulnerability_id].with_occurrence(
                    filename=filename, version=curr_version
                )
            else:
                vuln = Vulnerability(package, affected_versions, message).with_occurrence(
                    filename=filename, version=curr_version
                )
            self.ignored[vulnerability_id] = vuln
        else:
            if vulnerability_id in self.failed:
                vuln = self.failed[vulnerability_id].with_occurrence(
                    filename=filename, version=curr_version
                )
            else:
                vuln = Vulnerability(
                    package, affected_versions, message
                ).with_occurrence(filename=filename, version=curr_version)
            self.failed[vulnerability_id] = vuln


def check_json():
    """Runs `safety` on all requirements files and prints a summary of
    vulnerabilities in JSON format.  Always exits with a success code
    (0) unless the summary could not be generated.  Intended to
    produce JSON that other programs can consume an act upon
    appropriately.

    """
    check = SafetyCheck(IDS_TO_IGNORE)
    for filename in glob.glob('**/*requirements.txt', recursive=True):
        command = ['safety', 'check', '--json', '-r', filename]
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            output = e.output.decode('utf-8')
            sys.stderr.write(output)
            return 1
        for result in json.loads(result.stdout.decode('utf-8')):
            check.add(result, filename)

    print(check.to_json())
    return 0


def check_full_report():
    """Runs `safety` on all requirements files, outputs the full report
    for each.  Exits with a success code (0) if all the checks also
    executed with success, and exits with a failure code (1)
    otherwise.  Intended to be run in a CI context where the exit code
    of this command alone determines the pass/fail status of the
    overall check.

    """
    success = True
    command = ['safety', 'check', '--full-report']
    for ignored_id in IDS_TO_IGNORE:
        command.extend(['-i', ignored_id])
    for filename in glob.glob('**/*requirements.txt', recursive=True):
        print('Checking {}'.format(filename))
        result = subprocess.run(command + ['-r', filename])
        if result.returncode != 0:
            success = False
    return 0 if success else 1


def main(json_format=False):
    if json_format:
        return check_json()
    else:
        return check_full_report()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run a security audit of python packages'
    )
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    args = parser.parse_args()

    try:
        sys.exit(main(json_format=args.json))
    except Exception as e:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
