#!/bin/bash
#
# Write deployment version information to a file on disk

set -Eeuo pipefail

handle_error() {
    echo "Error: line $1, exit code $2" >&2
    exit 1
}

trap 'handle_error $LINENO $?' ERR

short_version_out="${DJANGO_SHORT_VERSION_FILE:-/deploy/version-short.txt}"
full_version_out="${DJANGO_FULL_VERSION_FILE:-/deploy/version-full.txt}"

# Check if we are inside a valid git repository
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch="$(git rev-parse --abbrev-ref HEAD)"
    commit="$(git rev-parse --verify HEAD)"

    case "$branch" in
        prod)
            branch_desc="on branch: ${branch}"
            ref_desc="release tag: $(git describe HEAD^2)";;
        HEAD)
            branch_desc="no branch, detached HEAD"
            ref_desc="not tagged, $(git describe --always --dirty)";;
        *)
            branch_desc="on branch: ${branch}"
            ref_desc="not tagged, $(git describe --always --dirty)";;
    esac

    git_history="$(git log -5 --oneline)"
else
    # Production images exclude .git, so the source branch and commit must be
    # supplied by the build. A missing tag is a valid, known state for branch
    # and pull-request builds rather than unknown provenance.
    : "${GIT_BRANCH:?GIT_BRANCH must be set when .git is unavailable}"
    : "${GIT_COMMIT_SHA:?GIT_COMMIT_SHA must be set when .git is unavailable}"
    branch_desc="on branch: ${GIT_BRANCH}"
    commit="${GIT_COMMIT_SHA}"
    if [[ -n "${GIT_TAG:-}" ]]; then
        ref_desc="release tag: ${GIT_TAG}"
    else
        ref_desc="not tagged"
    fi
    git_history="Git history was not embedded; metadata was supplied by build arguments."
fi

if [[ ! "$commit" =~ ^[0-9a-fA-F]{7,40}$ ]]; then
    echo "Invalid Git commit SHA: ${commit}" >&2
    exit 1
fi

# Trim commit to short hash if provided via environment variable
commit="${commit:0:7}"

# PATH selects the environment used by the application. PYTHON_BIN can override
# that without coupling this script to a particular virtualenv layout.
python_bin="${PYTHON_BIN:-python3}"
command -v "$python_bin" >/dev/null
python_version="$("$python_bin" --version 2>&1)"
python_deps="$("$python_bin" -m pip freeze)"
sys_info="$(cat /etc/*-release)"

echo "$commit" >"$short_version_out"

cat >"$full_version_out" <<EOF
#### GIT INFO ####

${branch_desc}
commit: ${commit}
${ref_desc}

${git_history}

#### PYTHON INFO ####

${python_version}

#### PYTHON DEPS ####

${python_deps}

#### SYS INFO ####

${sys_info}
EOF
