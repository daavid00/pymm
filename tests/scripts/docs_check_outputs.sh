files=(
    "test_outputs/docs_image/VTK_tracerTransport/tracerTransport_120.vtk"
    "test_outputs/docs_device/VTK_tracerTransport/tracerTransport_120.vtk"
)

missing_file="test_outputs/missing_docs_files.txt"
missing=0

rm -f "$missing_file"

for f in "${files[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "$f" >> "$missing_file"
        ((missing++))
    fi
done

if (( missing == 0 )); then
    echo "All figures and files exist."
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
fi
