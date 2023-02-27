FROM mambaorg/micromamba:1.3.1
RUN micromamba install -y -n base -c conda-forge coffea root && micromamba clean --all --yes

ENV input_file "initial_input.root"
ENV output_file "initial_output.root"

COPY /python /python

WORKDIR /python

CMD python3 -u run_bbWW_processing.py -i=$input_file -o=$output_file
