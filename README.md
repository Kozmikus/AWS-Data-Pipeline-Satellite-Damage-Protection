# AWS Data Pipeline Project about Satellite Protection/Damage Prevention for Large-scale Data Architectures Course

> Welcome to my **AWS Data Pipeline** project repository! 

This project is part of the "*Large-scale Data Architectures*" course. The goal of this project is to demonstrate the use of AWS resources for satellite damage protection and prevention, while also showcasing my skills in data engineering and cloud computing. The project utilizes various AWS services to create a robust data pipeline, creating business value for satellite operators, such as NASA.

## Datasets
The datasets used in this project are sourced from publicly available satellite telemetry data, specifically from:
- **Union of Concerned Scientists** (UCS, https://www.ucsusa.org/resources/satellite-database)
- **NASA US governmental free APIs** (https://api.nasa.gov/)

From the free APIs, one specific collection was used, the DONKI (Space Weather Database Of Notifications, Knowledge, Information) API. These datasets include information on satellite health, status, and environmental conditions that can impact satellite operations.

## Project Structure
To check the project structure and explanations, refer to the following files:
- `Project Outline.md`: Provides a detailed outline of the project, including objectives, methodology, and expected outcomes.
- `Results of Query Analysis.md`: Contains the results and analysis of queries performed on the datasets.

## AI Disclaimer
Some parts of this project have been assisted by AI tools to enhance quality and efficiency. However, all work has been reviewed and validated to ensure accuracy.
**Specifics**:
- GitHub Copilot was used to assist in writing down the reuslts of `Athena` queries in markdown table format quickly, found in the `Results of Query Analysis.md` file.
- Gemini 3.0 Pro was used to help with the initial challenges of the static CSV file transformations in Excel. Additionally, it assisted with specific Athena SQL functions (such as `CROSS JOIN UNNEST` and `FROM_ISO_8601_TIMESTAMP`) found on the internet that were new to me.