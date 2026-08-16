OUT="test_outputs/docs_device"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/activate_openfoam.sh
pymm -i examples/microsystem.png -o $OUT -p examples/parameters.toml -t all -m device
