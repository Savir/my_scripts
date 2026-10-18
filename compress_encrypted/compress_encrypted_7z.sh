#!/bin/bash

# 1. Check required env vars
if [[ -z "$TARGET_DIR" || -z "$ZIP_PASSWORD" ]]; then
  echo "❌ Error: TARGET_DIR and ZIP_PASSWORD must be set as environment variables."
  exit 1
fi

# 2. Normalize path (remove trailing slash, expand ~ and make it absolute)
TARGET_DIR="${TARGET_DIR%/}"
TARGET_DIR="$(eval echo "$TARGET_DIR")"  # expand
TARGET_DIR="$(realpath "$TARGET_DIR")"

# 3. Validate directory
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "❌ Error: Directory '$TARGET_DIR' does not exist."
  exit 1
fi

# 4. Change to TARGET_DIR
cd "$TARGET_DIR" || exit 1

# 5. Zip each subdir with relative path
for dir in */; do
  [[ -d "$dir" ]] || continue
  DIR_NAME="${dir%/}"
  ZIP_NAME="${DIR_NAME}.zip"

  echo "📦 Compressing $DIR_NAME -> $ZIP_NAME"
  if zip -r -P "$ZIP_PASSWORD" "$ZIP_NAME" "$DIR_NAME" -x "*/.DS_Store" "*/__MACOSX/*" &>/dev/null; then
    echo "✅ Created: $ZIP_NAME"
  else
    echo "❌ Failed: $ZIP_NAME"
  fi
done