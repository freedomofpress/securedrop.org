#!/bin/bash
#
# Print deployment version information; `--deploy` writes it to /deploy instead.
#
# The build context has no .git (and a worktree's .git points outside it), so
# `--build-args` emits the git facts on the host as build-args for a later,
# git-less run to relay. GIT_INFO_B64 is base64 because it spans lines.

# Keep to bash 3.2, which macOS ships as /bin/bash: no `inherit_errexit`, so no
# function whose failure matters may run inside `$(...)`.
set -euo pipefail
trap 'echo "Error: line ${LINENO}, exit code $?" >&2; exit 1' ERR

die() {
    echo "Error: $1" >&2
    shift
    [ $# -eq 0 ] || printf '  %s\n' "$@" >&2
    exit 1
}

case "${1:-}" in
    --build-args|--deploy) mode="${1#--}";;
    "") mode=print;;
    *)  die "unknown argument: $1" "Usage: $(basename "$0") [--build-args|--deploy]";;
esac

short_version_out="${DJANGO_SHORT_VERSION_FILE:-/deploy/version-short.txt}"
full_version_out="${DJANGO_FULL_VERSION_FILE:-/deploy/version-full.txt}"

# Set `commit` and `info` from live git. Assigns rather than prints, so errexit
# covers every git call here.
git_info() {
    local branch branch_desc ref_desc log recorded
    branch="$(git rev-parse --abbrev-ref HEAD)"
    # prod is special, in that we care what tag was merged in, rather that
    # what the merge commit is. --tags because release tags are lightweight;
    # --always lets a tag-less clone degrade to a SHA.
    case "$branch" in
        prod) branch_desc="on branch: ${branch}"
              ref_desc="release tag: $(git describe --tags HEAD^2)";;
        HEAD) branch_desc="no branch, detached HEAD"
              ref_desc="not tagged, $(git describe --always)";;
        *)    branch_desc="on branch: ${branch}"
              ref_desc="not tagged, $(git describe --always)";;
    esac
    commit="$(git rev-parse --short HEAD)"
    log="$(git log -5 --oneline)"
    # Build-args can go stale; date them.
    recorded="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    info="#### GIT INFO ####

${branch_desc}
commit: ${commit}
${ref_desc}
recorded: ${recorded}

${log}"
}

# Set `commit` and `info`, from live git or else from the relayed build-args.
facts() {
    if git rev-parse --git-dir >/dev/null 2>&1; then
        git_info
    elif [ "$mode" = build-args ]; then
        die "--build-args needs a git repository, and none was found here"
    elif [ -n "${GIT_COMMIT:-}" ] && [ -n "${GIT_INFO_B64:-}" ]; then
        commit="$GIT_COMMIT"
        info="$(base64 -d <<<"$GIT_INFO_B64")"
    else
        die "no git repository, and no GIT_COMMIT/GIT_INFO_B64 given" \
            "Run via: just dev, or just build-prod"
    fi
}

facts

# tr rather than `base64 -w0`, which macOS lacks.
if [ "$mode" = build-args ]; then
    echo "GIT_COMMIT=${commit}"
    echo "GIT_INFO_B64=$(printf '%s\n' "$info" | base64 | tr -d '\n')"
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
${info}

#### PYTHON INFO ####

$(python3 --version)

#### SYS INFO ####

$(cat /etc/*-release)
EOF
