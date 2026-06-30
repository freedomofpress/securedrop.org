#!/bin/bash
#
# Write deployment version information to a file on disk

set -e

handle_error() {
    echo "Error: line $1, exit code $2"
    exit 1
}

trap 'handle_error $LINENO $?' ERR

short_version_out="${DJANGO_SHORT_VERSION_FILE:-/deploy/version-short.txt}"
full_version_out="${DJANGO_FULL_VERSION_FILE:-/deploy/version-full.txt}"

# Check if we are inside a valid git repository
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch="$(git rev-parse --abbrev-ref HEAD)"
    commit="$(git rev-parse --short HEAD)"

    case "$branch" in
        prod)
            branch_desc="on branch: ${branch}"
            ref_desc="release tag: $(git describe HEAD^2 2>/dev/null || echo 'unknown tag')";;
        HEAD)
            branch_desc="no branch, detached HEAD"
            ref_desc="not tagged, $(git describe 2>/dev/null || echo 'unknown description')";;
        *)
            branch_desc="on branch: ${branch}"
            ref_desc="not tagged, $(git describe 2>/dev/null || echo 'unknown description')";;
    esac
    git_history="$(git log -5 --oneline)"
else
    # Fallbacks for when .git folder is missing (e.g., Production Docker builds)
    branch_desc="branch: ${GIT_BRANCH:-unknown (built without .git)}"
    commit="${GIT_COMMIT_SHA:-unknown}"
    ref_desc="tag/release: ${GIT_TAG:-unknown}"
    git_history="Git history unavailable in this build environment."
fi

# Trim commit to short hash if provided via environment variable
commit="${commit:0:7}"

echo "$commit" >"$short_version_out"

cat >"$full_version_out" <<EOF
#### GIT INFO ####

${branch_desc}
commit: ${commit}
${ref_desc}

${git_history}

#### PYTHON INFO ####

$(python3 --version)

#### PYTHON DEPS ####

$(poetry show --no-ansi --no-truncate)

#### SYS INFO ####

$(cat /etc/*-release)
EOF
