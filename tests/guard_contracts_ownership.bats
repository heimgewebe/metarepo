#!/usr/bin/env bats

load_lib() {
    # Mock git if needed or ensure environment
    true
}

setup() {
    # Create a temporary directory for the test repo
    TEST_DIR=$(mktemp -d)
    GUARD_SCRIPT="$BATS_TEST_DIRNAME/../guards/contracts_ownership.guard.sh"

    # Setup git repo in temp dir
    cd "$TEST_DIR"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"

    # Initial commit to allow diffs
    touch README.md
    git add README.md
    git commit -m "Initial commit" -q
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "PASSES: Repo ≠ metarepo/≠ contracts-mirror and no contracts/** changes" {
    export HG_REPO_NAME="some-satellite"
    touch logic.py
    git add logic.py

    run "$GUARD_SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Repo is some-satellite"* ]]
    [[ "$output" == *"OK"* ]]
}

@test "FAILS: Repo ≠ metarepo/≠ contracts-mirror and contracts/foo.schema.json in Diff" {
    export HG_REPO_NAME="some-satellite"
    mkdir -p contracts
    touch contracts/foo.schema.json
    git add contracts/foo.schema.json

    run "$GUARD_SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Contracts Ownership Violation"* ]]
    [[ "$output" == *"metarepo/contracts"* ]]
}

@test "PASSES: Repo == metarepo, fleet/repos.yml vorhanden" {
    export HG_REPO_NAME="metarepo"
    mkdir -p fleet contracts
    touch fleet/repos.yml
    touch contracts/decision.outcome.v1.schema.json
    git add fleet/repos.yml contracts/decision.outcome.v1.schema.json

    run "$GUARD_SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Repo is metarepo"* ]]
    [[ "$output" == *"Contracts modification allowed"* ]]
}

@test "FAILS: Repo == metarepo, fleet/repos.yml fehlt" {
    export HG_REPO_NAME="metarepo"
    # Ensure fleet/repos.yml is NOT there
    touch other.file
    git add other.file

    run "$GUARD_SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Integrity violation"* ]]
    [[ "$output" == *"fleet/repos.yml"* ]]
}

@test "FAILS: Repo == contracts-mirror, contracts/** changed" {
    export HG_REPO_NAME="contracts-mirror"
    mkdir -p contracts
    touch contracts/internal.schema.json
    git add contracts/internal.schema.json

    run "$GUARD_SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"contracts-mirror' must not modify internal"* ]]
}

@test "PASSES: Repo == contracts-mirror, json/** changed" {
    export HG_REPO_NAME="contracts-mirror"
    mkdir -p json
    touch json/external.schema.json
    git add json/external.schema.json

    run "$GUARD_SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Repo is contracts-mirror"* ]]
    [[ "$output" == *"OK"* ]]
}

@test "PASSES: No changes detected" {
    export HG_REPO_NAME="any-repo"
    # No changes staged
    run "$GUARD_SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"No changed files detected"* ]]
}

@test "PASSES: Detected as metarepo via filesystem (no env var)" {
    unset HG_REPO_NAME
    mkdir -p fleet contracts
    touch fleet/repos.yml
    touch contracts/test.json
    git add fleet/repos.yml contracts/test.json

    run "$GUARD_SCRIPT"
    [ "$status" -eq 0 ]
    # Since we are in a temp dir with no remote, it falls back to toplevel basename.
    # The basename of mktemp -d is random, e.g., tmp.XXXX.
    # But the script sets IS_METAREPO=true if fleet/repos.yml exists.
    # Wait, the script logic is:
    # if IS_METAREPO=true -> exit 0.
    # It does NOT rely on REPO_NAME being "metarepo" for the allow-all check, only for the integrity check.
    [[ "$output" == *"Contracts modification allowed"* ]]
}
