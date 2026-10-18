#!/bin/bash

set -e

ROOT_DIR="$1"

if [[ -z "$ROOT_DIR" ]]; then
    echo "Usage: $0 /path/to/root/directory"
    exit 1
fi

if [[ ! -d "$ROOT_DIR" ]]; then
    echo "Directory does not exist: $ROOT_DIR"
    exit 1
fi

read -s -p "Password: " PASSWORD
echo
read -s -p "Confirm password: " PASSWORD2
echo

if [[ "$PASSWORD" != "$PASSWORD2" ]]; then
    echo "Passwords do not match."
    exit 1
fi

cd "$ROOT_DIR"

for dir in */; do
    [[ -d "$dir" ]] || continue

    name="${dir%/}"

    echo "Encrypting: $name"

    zip -r -P "$PASSWORD" "${name}.zip" "$name"
done

unset PASSWORD PASSWORD2
