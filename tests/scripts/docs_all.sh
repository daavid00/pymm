# Run as . tests/scripts/docs_all.sh
. tests/scripts/docs_image.sh &
. tests/scripts/docs_device.sh &
wait

. tests/scripts/docs_check_outputs.sh
