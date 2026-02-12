# MSDS PoC (Multi-Source Data System - Proof of Concept)

[![GitHub](assets/github_icon.svg)](https://github.com/jaeho-david-lim/msds-poc)

A proof-of-concept implementation for a Multi-Source Data System designed to aggregate and process data from multiple sources efficiently.

## 📋 Project Overview

MSDS PoC demonstrates the core architecture and workflows for managing multi-source data ingestion, transformation, and output generation. This PoC provides a foundation for building scalable data pipeline systems.

## 🚀 Features

- **Multi-source data ingestion**: Support for various data sources
- **Data transformation pipeline**: Flexible data processing capabilities
- **Modular architecture**: Easy to extend and customize
- **Smoke testing**: Automated testing suite for validation
- **Configuration management**: Environment-based configuration support

## 📁 Project Structure

```
msds-poc/
├── msds_poc/              # Main Python package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Core PoC execution logic
│   └── utils.py           # Utility functions
├── scripts/               # Utility scripts
│   └── smoke_test.sh      # Smoke test suite
├── input/                 # Input data directory
├── output/                # Output results directory
├── assets/                # Assets (icons, images, etc.)
│   ├── github_icon.svg    # GitHub icon
│   └── s_icon.svg         # S icon placeholder
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip or conda package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jaeho-david-lim/msds-poc.git
cd msds-poc
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

## 🧪 Running Smoke Tests

Execute the smoke test suite to verify the installation:

```bash
bash scripts/smoke_test.sh
```

This will verify:
- Python availability
- Dependencies installation
- Basic PoC execution
- Directory structure validation

## 📝 Usage

### Basic PoC Execution

```python
from msds_poc import run_poc

result = run_poc()
print(result)
```

### Using Command Line

```bash
python3 -m msds_poc.main
```

## 📊 Input and Output

- **Input directory**: `input/`  
  Place raw data files here for processing
  
- **Output directory**: `output/`  
  Processed results are saved here

## 🔧 Configuration

Edit `.env.example` and save as `.env` to configure:

```bash
cp .env.example .env
```

Available settings:
- `APP_ENV`: Application environment (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `INPUT_DIR`: Input data directory path
- `OUTPUT_DIR`: Output results directory path
- `DATA_SOURCE_TIMEOUT`: Data source timeout in seconds

## 📦 Dependencies

Core dependencies:
- `python-dotenv`: Environment variable management
- `click`: CLI framework

Development tools:
- `pytest`: Testing framework
- `black`: Code formatter
- `flake8`: Linting
- `mypy`: Type checking

See `requirements.txt` or `pyproject.toml` for full list.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- MSDS Team

## 🆘 Support

For issues and questions, please open a GitHub issue.
