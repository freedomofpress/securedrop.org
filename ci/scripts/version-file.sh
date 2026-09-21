#!/bin/bash
#
# Print deployment version information; `--deploy` writes it to /deploy instead.
#
# The build context has no .git (and a worktree's .git points outside it), so
# `--dump` records git facts on the host for a later, git-less run to relay.

set -euo pipefail
trap 'echo "Error: line ${LINENO}, exit code $?" >&2; exit 1' ERR

die() {
    echo "Error: $1" >&2
    shift
    [ $# -eq 0 ] || printf '  %s\n' "$@" >&2
    exit 1
}

case "${1:-}" in
    --dump|--deploy) mode="${1#--}";;
    "") mode=print;;
    *)  die "unknown argument: $1" "Usage: $(basename "$0") [--dump|--deploy]";;
esac

short_version_out="${DJANGO_SHORT_VERSION_FILE:-/deploy/version-short.txt}"
full_version_out="${DJANGO_FULL_VERSION_FILE:-/deploy/version-full.txt}"
# Relative to this script: it runs from /ci/scripts in the build, ./ci/scripts in dev.
facts_file="$(dirname "$0")/../version/git-facts.sh"

if git rev-parse --git-dir >/dev/null 2>&1; then
    branch="$(git rev-parse --abbrev-ref HEAD)"
    commit="$(git rev-parse --short HEAD)"
    # prod is special, in that we care what tag was merged in, rather that
    # what the merge commit is. --always lets a tag-less clone degrade to a SHA.
    case "$branch" in
        prod) branch_desc="on branch: ${branch}"
              ref_desc="release tag: $(git describe HEAD^2)";;
        HEAD) branch_desc="no branch, detached HEAD"
              ref_desc="not tagged, $(git describe --always)";;
        *)    branch_desc="on branch: ${branch}"
              ref_desc="not tagged, $(git describe --always)";;
    esac
    recent_log="$(git log -5 --oneline)"
    # A dump can go stale; date it.
    recorded_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
elif [ "$mode" = dump ]; then
    die "--dump needs a git repository, and none was found here"
elif [ -r "$facts_file" ]; then
    # shellcheck source=/dev/null
    . "$facts_file"
else
    die "no git repository, and no dumped facts at ${facts_file}" \
        "Dump them first: ci/scripts/version-file.sh --dump"
fi

# %q survives the newlines in recent_log, so the dump round-trips exactly.
if [ "$mode" = dump ]; then
    mkdir -p "$(dirname "$facts_file")"
    for v in commit branch_desc ref_desc recent_log recorded_at; do
        printf '%s=%q\n' "$v" "${!v}"
    done >"$facts_file"
    exit 0
fi

if [ "$mode" = deploy ]; then
    echo "$commit" >"$short_version_out"
    exec >"$full_version_out"
fi

# No python dependency section: this report is generated in a build stage that
# has none of the app's dependencies installed, so a "pip freeze" here would
# describe a bare interpreter. The authoritative pinned set is requirements.txt,
# shipped in the image and installed with --no-deps --require-hashes.
cat <<EOF
#### GIT INFO ####

${branch_desc}
commit: ${commit}
${ref_desc}
recorded: ${recorded_at}

${recent_log}

#### PYTHON INFO ####

$(python3 --version)

#### SYS INFO ####

$(cat /etc/*-release)
EOF
