docker run --rm -v $(pwd)/input_files:/python/input_files -v$(pwd)/output_files:/python/output_files -e input_file=input_files/run2022C_data_doublemuon_nanoaod.root -e output_file=output_files/out_run2022C_data_doublemuon_nanoaod.root run3_bbww