# Shree's Quant Codespaces ♥️ 

Bunch of useful Jupyter Notebooks & Streamlit Apps
  -    US markets dashboard
  -    India markets dashboard

Bunch of Streamlit apps

# How to Run the stream app?
make sure you have docker (installed and path-configured to run the command) and an internet connection
(to pull images from public registry, yfinance package installation , etc)

  - docker build -t quant_apps . 
  - docker run -p 9000:9000 quant_apps
  - localhost:9000  #### (in your browser)
