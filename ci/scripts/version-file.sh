#!/bin/bash
#
#
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

branch="$(git rev-parse --abbrev-ref HEAD)"
commit="$(git rev-parse --short HEAD)"

# prod is special, in that we care what tag was merged in, rather that
# what the merge commit is.
case "$branch" in
    prod)
        branch_desc="on branch: ${branch}"
        ref_desc="release tag: $(git describe HEAD^2)";;
    HEAD)
        branch_desc="no branch, detached HEAD"
        ref_desc="not tagged, $(git describe)";;
    *)
        branch_desc="on branch: ${branch}"
        ref_desc="not tagged, $(git describe)";;
esac

echo "$commit" >"$short_version_out"

# No python dependency section: this report is generated in a build stage that
# has none of the app's dependencies installed, so a "pip freeze" here would
# describe a bare interpreter. The authoritative pinned set is requirements.txt,
# shipped in the image and installed with --no-deps --require-hashes.
cat >"$full_version_out" <<EOF
#### GIT INFO ####

${branch_desc}
commit: ${commit}
${ref_desc}

$(git log -5 --oneline)

#### PYTHON INFO ####

$(python3 --version)

#### SYS INFO ####

$(cat /etc/*-release)
EOF
