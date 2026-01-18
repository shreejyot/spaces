FROM mcr.microsoft.com/devcontainers/miniconda:latest

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt

RUN conda create -n quant_tools python=3.11 pip -y && \
    conda run -n quant_tools pip install --no-cache-dir -r /app/requirements.txt


COPY ../data /app/data
COPY ../streamlit_apps /app/streamlit_apps
COPY ../notebooks /app/notebooks
COPY ../run_streamlit.sh /app/run_streamlit.sh
RUN chmod +x /app/run_streamlit.sh

### Everything above this is run on docker build.
### Run on docker run. 
#CMD ["conda activate quant_tools && sh /app/run_streamlit.sh"]
# Activate the environment 'myenv' and run the script
CMD ["conda", "run", "-n", "quant_tools", "bash", "/app/run_streamlit.sh"]