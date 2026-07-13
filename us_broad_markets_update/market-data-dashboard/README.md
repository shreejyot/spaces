# Market Data Dashboard

This project is a Streamlit application that visualizes market data for various indices. It allows users to select a date range and view the corresponding market trends through interactive charts.

## Project Structure

```
market-data-dashboard
├── src
│   ├── app.py                # Main entry point of the Streamlit application
│   ├── data
│   │   └── us_indices_data.csv # Contains market indices data
│   └── utils
│       └── fetch_data.py     # Utility function to fetch market data
├── requirements.txt           # Lists project dependencies
└── README.md                  # Project documentation
```

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd market-data-dashboard
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Streamlit application, execute the following command in your terminal:

```
streamlit run src/app.py
```

Once the application is running, you can access it in your web browser at `http://localhost:8501`.

## Features

- **Date Range Selection**: Users can select a start date and an end date to filter the market data.
- **Interactive Charts**: The application generates charts displaying the closing prices of various market indices over the selected date range.
- **Data Source**: The application uses data from Yahoo Finance, fetched through the `yfinance` library.

## Dependencies

The project requires the following Python packages:

- `streamlit`
- `yfinance`
- `pandas`
- `matplotlib`

Make sure to install these packages using the `requirements.txt` file.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.