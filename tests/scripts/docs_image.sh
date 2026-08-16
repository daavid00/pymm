OUT="test_outputs/docs_image"
. tests/scripts/initialize_output_folders.sh $OUT
pymm -i examples/microsystem.png -o $OUT -p examples/parameters.toml -t all
