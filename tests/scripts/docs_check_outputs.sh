files="
test_outputs/docs_image/VTK_tracerTransport/tracerTransport_120.vtk
test_outputs/docs_device/VTK_tracerTransport/tracerTransport_120.vtk
"

missing_file="test_outputs/missing_docs_files.txt"
missing=0

rm -f "$missing_file"

for f in $files; do
    if [ ! -f "$f" ]; then
        echo "$f" >> "$missing_file"
        missing=$((missing + 1))
    fi
done

if [ "$missing" -eq 0 ]; then
    echo "All figures and files exist."
    return 0
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
    return 1
fi
