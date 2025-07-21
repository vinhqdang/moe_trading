# Mixture of Experts (MoE) Trading System

This project implements a Mixture of Experts (MoE) system where multiple expert algorithms collaborate to develop trading strategies. The experts meet to discuss their analyses, reach consensus, and then backtest their strategies with real market data. After each round, experts learn from performance feedback and adapt their strategies.

## Performance Summary

In our latest test, the MOE system showed:

| Round | MOE Performance | S&P 500 Performance | Difference |
|-------|----------------|---------------------|------------|
| 1     | 0.59%          | -0.65%              | +1.24%     |
| 2     | 0.88%          | 2.95%               | -2.07%     |
| **Average** | **0.73%** | **1.15%**          | **-0.42%** |

Key observations:
- The system showed **continuous improvement** with returns increasing from 0.59% to 0.88%
- Performance was more **consistent** than S&P 500 despite changing market conditions
- The experts successfully collaborated through sophisticated discussions to reach consensus

See [performance_analysis.md](./performance_analysis.md) for detailed analysis.

## Features

- **Multiple Expert Strategies**: Includes trend following, mean reversion, volatility-based, and sentiment analysis experts
- **Expert Meetings**: Simulated discussions between experts to reach consensus
- **AI-Generated Discussions**: Uses OpenAI GPT or Google Gemini APIs to generate realistic expert discussions
- **Backtesting Framework**: Tests strategies against historical market data
- **Learning Mechanism**: Experts adapt their strategies based on performance
- **Configurable Parameters**: Adjustable meeting rounds, learning rounds, and testing periods

## Requirements

- Python 3.7+
- Required Python packages:
  - pandas
  - numpy
  - openai
  - google-generativeai
  - yfinance (for S&P 500 comparison)
  - matplotlib (for visualization, optional)

## Installation

1. Clone the repository

2. Use the setup script (easiest method):

```bash
./setup.sh
```

Or choose one of the following manual installation methods:

### Using pip

```bash
pip install -r requirements.txt
```

### Using conda (recommended for reproducibility)

```bash
# Create and activate the conda environment
conda env create -f environment.yml
conda activate moe_trading

# Verify installation
python verify_setup.py
```

3. Set up your API keys:

   Copy the example config file and add your API keys:
   
   ```bash
   cp config.json.example config.json
   # Edit config.json and add your API keys
   ```
   
   The config.json file should look like this (with your actual keys):
   
   ```json
   {
       "openai_api_key": "your_openai_api_key_here",
       "gemini_api_key": "your_gemini_api_key_here"
   }
   ```
   
   Note: config.json is git-ignored to prevent accidentally committing API keys.

## Usage

### Command Line

Run the system with default settings:

```bash
python main.py
```

Or customize the parameters:

```bash
python main.py --rounds 5 --meeting-rounds 3 --test-days 30 --train-days 180
```

### Jupyter Notebook

For an interactive experience, you can use the included demo notebook:

```bash
jupyter notebook demo.ipynb
```

The notebook demonstrates:
- Running the MOE system
- Comparing with S&P 500 performance
- Visualizing the results
- Analyzing expert meeting discussions

### Command-line Arguments

- `--rounds`: Number of learning rounds (default: 3)
- `--meeting-rounds`: Maximum number of discussion rounds per meeting (default: 3)
- `--test-days`: Number of days for backtesting period (default: 30)
- `--train-days`: Number of days for training data (default: 180)

## System Components

- `expert.py`: Base expert class
- `strategies.py`: Different expert strategies
- `meeting.py`: Expert meeting and consensus mechanism
- `backtester.py`: Backtesting framework
- `main.py`: Main program flow
- `benchmark_comparison.py`: Compare MOE performance with S&P 500
- `simple_compare.py`: Simplified performance comparison script
- `performance_analysis.md`: Detailed performance analysis

## How It Works

1. **Initialization**: Create experts with different strategies
2. For each learning round:
   - **Data Collection**: Get training and testing data
   - **Expert Analysis**: Each expert analyzes the data
   - **Expert Meeting**: Experts discuss and try to reach consensus
   - **Backtesting**: Test the consensus strategy against market data
   - **Learning**: Experts update their strategies based on performance
3. **Evaluation**: Performance summary across all rounds

## Meeting Process

1. Each expert provides their initial recommendation with confidence level
2. Experts discuss for up to `k` rounds, trying to persuade each other
3. If consensus is reached, the meeting ends
4. If no consensus after `k` rounds, a weighted voting mechanism is used

## Output Files

- `moe_system.log`: System log file
- `meeting_logs.log`: Detailed meeting logs
- `meeting_log_*.json`: JSON files with meeting discussions for each round
- `backtest_results_*.json`: Backtest results for each round
- `moe_summary_results.json`: Overall performance summary

## Customization

You can extend the system by:
- Adding new expert types in `strategies.py`
- Modifying the consensus algorithm in `meeting.py`
- Enhancing the backtesting framework in `backtester.py`
- Adding visualization tools for results analysis

## License

This project is open-source and available under the MIT License.