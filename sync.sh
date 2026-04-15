#!/usr/bin/env bash
# sync.sh — Synchronize SKILL.md files between ~/.agents/skills and ~/.claude/skills,
#           then commit any changes to the skills git repository.
# Skips skill directories that begin with the "pvt-" prefix.

set -euo pipefail

COPILOT_DIR="$HOME/.agents/skills"
CLAUDE_DIR="$HOME/.claude/skills"
GIT_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Collect unique skill names from both source directories, separated by type
PUBLIC_SKILLS=$( {
    for dir in "$COPILOT_DIR"/*/; do
        [[ -d "$dir" ]] || continue
        skill=$(basename "$dir")
        [[ "$skill" == pvt-* ]] && continue
        echo "$skill"
    done
    for dir in "$CLAUDE_DIR"/*/; do
        [[ -d "$dir" ]] || continue
        skill=$(basename "$dir")
        [[ "$skill" == pvt-* ]] && continue
        echo "$skill"
    done
} | sort -u )

PRIVATE_SKILLS=$( {
    for dir in "$COPILOT_DIR"/*/; do
        [[ -d "$dir" ]] || continue
        skill=$(basename "$dir")
        [[ "$skill" == pvt-* ]] || continue
        echo "$skill"
    done
    for dir in "$CLAUDE_DIR"/*/; do
        [[ -d "$dir" ]] || continue
        skill=$(basename "$dir")
        [[ "$skill" == pvt-* ]] || continue
        echo "$skill"
    done
} | sort -u )

SKILLS=$(echo -e "$PUBLIC_SKILLS\n$PRIVATE_SKILLS" | grep -v '^$' | sort -u)

if [[ -z "$SKILLS" ]]; then
    echo "No skills found to sync."
    exit 0
fi

while IFS= read -r skill; do
    copilot_file="$COPILOT_DIR/$skill/SKILL.md"
    claude_file="$CLAUDE_DIR/$skill/SKILL.md"

    copilot_exists=false
    claude_exists=false
    [[ -f "$copilot_file" ]] && copilot_exists=true
    [[ -f "$claude_file" ]]  && claude_exists=true

    if $copilot_exists && $claude_exists; then
        # Both exist — copy the newer one to the other location
        if [[ "$copilot_file" -nt "$claude_file" ]]; then
            echo "[sync] $skill: copilot -> claude (copilot is newer)"
            cp "$copilot_file" "$claude_file"
        elif [[ "$claude_file" -nt "$copilot_file" ]]; then
            echo "[sync] $skill: claude -> copilot (claude is newer)"
            cp "$claude_file" "$copilot_file"
        else
            echo "[ok]   $skill: already in sync"
        fi
    elif $copilot_exists; then
        echo "[sync] $skill: copilot -> claude (new)"
        mkdir -p "$CLAUDE_DIR/$skill"
        cp "$copilot_file" "$claude_file"
    elif $claude_exists; then
        echo "[sync] $skill: claude -> copilot (new)"
        mkdir -p "$COPILOT_DIR/$skill"
        cp "$claude_file" "$copilot_file"
    fi

    # Update the git repo with the now-synced SKILL.md (public skills only)
    if [[ "$skill" != pvt-* ]]; then
        mkdir -p "$GIT_REPO/$skill"
        if [[ -f "$claude_file" ]]; then
            cp "$claude_file" "$GIT_REPO/$skill/SKILL.md"
        elif [[ -f "$copilot_file" ]]; then
            cp "$copilot_file" "$GIT_REPO/$skill/SKILL.md"
        fi
    fi
done <<< "$SKILLS"

# Commit any changes in the git repo
cd "$GIT_REPO"
git add .

if git diff --cached --quiet; then
    echo ""
    echo "Git repo: nothing to commit — all skills up to date."
else
    git commit -m "Sync skills: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "Git repo: changes committed."
fi

git push
echo "Git repo: pushed to remote."
