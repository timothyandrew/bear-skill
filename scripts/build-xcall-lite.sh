#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SWIFT_SRC="$SCRIPT_DIR/xcall-lite.swift"
APP_BUNDLE="$SCRIPT_DIR/xcall-lite.app"
BINARY="$APP_BUNDLE/Contents/MacOS/xcall-lite"
PLIST_SRC="$SCRIPT_DIR/Info.plist"
PLIST_DST="$APP_BUNDLE/Contents/Info.plist"

# Check if rebuild is needed
if [ -f "$BINARY" ] && [ -f "$PLIST_DST" ]; then
    if [ "$SWIFT_SRC" -ot "$BINARY" ] && [ "$PLIST_SRC" -ot "$PLIST_DST" ]; then
        echo "xcall-lite is up to date."
        exit 0
    fi
fi

echo "Building xcall-lite..."

# Create .app bundle structure
mkdir -p "$APP_BUNDLE/Contents/MacOS"

# Copy Info.plist
cp "$PLIST_SRC" "$PLIST_DST"

# Compile
swiftc "$SWIFT_SRC" -o "$BINARY" -framework Cocoa

# Register with LaunchServices so macOS knows about the URL scheme
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -R "$APP_BUNDLE"

echo "xcall-lite built and registered successfully."
