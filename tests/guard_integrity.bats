#!/usr/bin/env bats

setup() {
  export WGX_PROJECT_ROOT="$(cd "${BATS_TEST_DIRNAME}/.." && pwd)"
  export PATH="$WGX_PROJECT_ROOT/tools/bin:$PATH"
  export GUARD_SCRIPT="$WGX_PROJECT_ROOT/wgx/guards/integrity.bash"
  export PAYLOAD_DIR="$WGX_PROJECT_ROOT/reports/integrity"
  mkdir -p "$PAYLOAD_DIR"
}

teardown() {
  rm -rf "$WGX_PROJECT_ROOT/reports/integrity"
}

@test "Guard fails when payload is missing" {
  rm -f "$PAYLOAD_DIR/event_payload.json"
  run bash "$GUARD_SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "MISSING"|"FAIL" ]]
}

@test "Guard passes with valid payload" {
  cat > "$PAYLOAD_DIR/event_payload.json" <<EOF
{
  "url": "https://example.com",
  "generated_at": "2023-01-01T00:00:00Z",
  "repo": "heimgewebe/wgx",
  "status": "OK"
}
EOF
  run bash "$GUARD_SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "OK" ]]
}

@test "Guard fails with forbidden 'counts' key" {
  cat > "$PAYLOAD_DIR/event_payload.json" <<EOF
{
  "url": "https://example.com",
  "generated_at": "2023-01-01T00:00:00Z",
  "repo": "heimgewebe/wgx",
  "status": "OK",
  "counts": { "errors": 0 }
}
EOF
  run bash "$GUARD_SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "forbidden" ]]
}

@test "Guard fails with missing mandatory key" {
  cat > "$PAYLOAD_DIR/event_payload.json" <<EOF
{
  "generated_at": "2023-01-01T00:00:00Z",
  "repo": "heimgewebe/wgx",
  "status": "OK"
}
EOF
  run bash "$GUARD_SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "Missing mandatory key" ]]
}

@test "Guard fails with invalid status" {
  cat > "$PAYLOAD_DIR/event_payload.json" <<EOF
{
  "url": "https://example.com",
  "generated_at": "2023-01-01T00:00:00Z",
  "repo": "heimgewebe/wgx",
  "status": "INVALID_STATUS"
}
EOF
  run bash "$GUARD_SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "Invalid status" ]]
}
