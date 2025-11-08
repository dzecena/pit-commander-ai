# Open Source Credits

This project was built using the following open source projects, libraries, and tools. We are grateful to the open source community for making these resources available.

## Core Programming Languages

### Python 3.x
- **License**: Python Software Foundation License
- **Website**: https://www.python.org/
- **Usage**: Primary language for data processing, analysis, and automation scripts

### JavaScript (ES6+)
- **License**: Open standard (ECMA-262)
- **Usage**: Frontend dashboard interactivity and data visualization

### HTML5 & CSS3
- **License**: Open web standards (W3C)
- **Usage**: Dashboard structure and styling

## Python Libraries

### Data Processing & Analysis

**Pandas** (v2.1.0+)
- **License**: BSD 3-Clause License
- **Website**: https://pandas.pydata.org/
- **Usage**: Telemetry data manipulation, cleaning, and analysis
- **Why we use it**: Industry-standard library for handling CSV data and time-series analysis

**NumPy** (v1.24.3)
- **License**: BSD 3-Clause License
- **Website**: https://numpy.org/
- **Usage**: Statistical calculations, performance metrics, and numerical operations
- **Why we use it**: Fast array operations for lap time analysis and consistency calculations

**PyArrow** (v13.0.0)
- **License**: Apache License 2.0
- **Website**: https://arrow.apache.org/docs/python/
- **Usage**: Efficient data serialization and columnar data processing
- **Why we use it**: High-performance data interchange format

### Machine Learning

**scikit-learn** (v1.3.0)
- **License**: BSD 3-Clause License
- **Website**: https://scikit-learn.org/
- **Usage**: Pattern recognition in driver performance and predictive analytics
- **Why we use it**: Robust machine learning algorithms for performance prediction

**joblib** (v1.3.2)
- **License**: BSD 3-Clause License
- **Website**: https://joblib.readthedocs.io/
- **Usage**: Model persistence and parallel processing
- **Why we use it**: Efficient caching and parallel computation

### Data Visualization

**Matplotlib** (v3.7.2)
- **License**: PSF-based License
- **Website**: https://matplotlib.org/
- **Usage**: Track visualization and performance charts
- **Why we use it**: Flexible plotting library for custom visualizations

**Seaborn** (v0.12.2)
- **License**: BSD 3-Clause License
- **Website**: https://seaborn.pydata.org/
- **Usage**: Statistical data visualization and heatmaps
- **Why we use it**: Beautiful statistical graphics with minimal code

**Plotly** (v5.17.0)
- **License**: MIT License
- **Website**: https://plotly.com/python/
- **Usage**: Interactive charts and graphs
- **Why we use it**: Interactive visualizations for detailed analysis

### Cloud & Infrastructure

**Boto3** (v1.28.25+)
- **License**: Apache License 2.0
- **Website**: https://boto3.amazonaws.com/
- **Usage**: AWS S3 integration for dashboard deployment
- **Why we use it**: Official AWS SDK for Python

**AWS CLI** (v1.29.25)
- **License**: Apache License 2.0
- **Website**: https://aws.amazon.com/cli/
- **Usage**: Command-line deployment and cloud management
- **Why we use it**: Automated deployment scripts

### Web Framework & API

**FastAPI** (v0.103.0+)
- **License**: MIT License
- **Website**: https://fastapi.tiangolo.com/
- **Usage**: API endpoints for data access (future enhancement)
- **Why we use it**: Modern, fast web framework with automatic API documentation

**Uvicorn** (v0.23.2+)
- **License**: BSD 3-Clause License
- **Website**: https://www.uvicorn.org/
- **Usage**: ASGI server for FastAPI applications
- **Why we use it**: High-performance async server

**Mangum** (v0.17.0)
- **License**: MIT License
- **Website**: https://mangum.io/
- **Usage**: AWS Lambda adapter for ASGI applications
- **Why we use it**: Serverless deployment of FastAPI apps

### Dashboard Components

**Dash** (v2.14.2)
- **License**: MIT License
- **Website**: https://dash.plotly.com/
- **Usage**: Interactive dashboard components
- **Why we use it**: Python-based dashboard framework

**Dash Bootstrap Components** (v1.5.0)
- **License**: Apache License 2.0
- **Website**: https://dash-bootstrap-components.opensource.faculty.ai/
- **Usage**: Responsive dashboard layouts
- **Why we use it**: Bootstrap styling for Dash applications

### Utilities

**python-dotenv** (v1.0.0)
- **License**: BSD 3-Clause License
- **Website**: https://github.com/theskumar/python-dotenv
- **Usage**: Environment variable management
- **Why we use it**: Secure configuration management

**tqdm** (v4.66.1)
- **License**: MIT License / MPL-2.0
- **Website**: https://tqdm.github.io/
- **Usage**: Progress bars for data processing
- **Why we use it**: User-friendly progress indicators

**Pydantic** (v2.5.0)
- **License**: MIT License
- **Website**: https://docs.pydantic.dev/
- **Usage**: Data validation and settings management
- **Why we use it**: Type-safe data validation

**Jinja2** (v3.1.2)
- **License**: BSD 3-Clause License
- **Website**: https://jinja.palletsprojects.com/
- **Usage**: Template rendering for reports
- **Why we use it**: Powerful templating engine

**WebSockets** (v11.0.3)
- **License**: BSD 3-Clause License
- **Website**: https://websockets.readthedocs.io/
- **Usage**: Real-time data streaming (future enhancement)
- **Why we use it**: Async WebSocket implementation

**python-multipart** (v0.0.6)
- **License**: Apache License 2.0
- **Website**: https://github.com/andrew-d/python-multipart
- **Usage**: File upload handling
- **Why we use it**: Multipart form data parsing

## Development Tools

**Git**
- **License**: GPL v2
- **Website**: https://git-scm.com/
- **Usage**: Version control and collaboration

**GitHub**
- **Website**: https://github.com/
- **Usage**: Code hosting and project management

**Jupyter Notebook**
- **License**: BSD 3-Clause License
- **Website**: https://jupyter.org/
- **Usage**: Data exploration and prototyping

## Cloud Services

**Amazon Web Services (AWS)**
- **Service**: S3 (Simple Storage Service)
- **Website**: https://aws.amazon.com/s3/
- **Usage**: Static dashboard hosting and data storage
- **Why we use it**: Reliable, scalable cloud storage

## Fonts & Icons

**Segoe UI Font**
- **License**: Microsoft Typography License
- **Usage**: Dashboard typography
- **Note**: System font, no distribution

**Unicode Emoji**
- **License**: Unicode License
- **Usage**: Visual indicators (🏁, 🏎️, 📊, 🎯, etc.)
- **Note**: Standard Unicode characters

## Data Sources

**Toyota GR Cup Telemetry Data**
- **Source**: Real racing telemetry from GR Cup series
- **Usage**: Performance analysis and coaching insights
- **Note**: Anonymized driver data

**Track Layout Documentation**
- **Source**: Official track maps from racing circuits
- **Usage**: Visual track representation in dashboards
- **Tracks**: Barber, COTA, VIR, Sebring, Sonoma, Road America, Indianapolis

## Standards & Protocols

**HTTP/HTTPS**
- **Standard**: IETF RFC 2616 / RFC 2818
- **Usage**: Web communication

**JSON**
- **Standard**: ECMA-404
- **Usage**: Data interchange format

**CSV**
- **Standard**: RFC 4180
- **Usage**: Telemetry data format

## Special Thanks

We would like to extend special thanks to:

- **The Python Software Foundation** for maintaining Python and its ecosystem
- **The Pandas Development Team** for creating the best data analysis library
- **The AWS Team** for providing reliable cloud infrastructure
- **The Open Source Community** for countless contributions that made this project possible

## License Compliance

All open source components used in this project are in compliance with their respective licenses. This project respects and adheres to:

- BSD 3-Clause License terms
- MIT License terms
- Apache License 2.0 terms
- Python Software Foundation License terms

## Contributing Back

We believe in giving back to the open source community. If you find this project useful, please consider:
- Contributing to the libraries we use
- Sharing your improvements
- Supporting open source projects financially
- Teaching others about open source

## Disclaimer

All trademarks, service marks, and company names are the property of their respective owners. This project is not officially affiliated with or endorsed by Toyota, GR Cup, or any racing organization.

---

**Last Updated**: November 2025

For questions about licensing or credits, please open an issue on our GitHub repository.
