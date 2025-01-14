#!/bin/bash
set -eu

target_dir=$(dirname $(realpath $0))
script=$(realpath ${1:?})

shift
for toolchain in $target_dir/toolchains/*; do
    $script $toolchain "$@"
done
