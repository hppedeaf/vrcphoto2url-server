# Server Setup Instructions

## Prerequisites

Before setting up the server application, ensure you have the following installed:

- Python 3.7 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Project Structure

The server application is organized into the following structure:

```
server/
├── src/
│   ├── app.py
│   ├── config/
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── utils/
├── requirements.txt
├── railway.json
├── Procfile
└── README.md
```

## Installation Steps

1. **Clone the Repository**

   Clone the project repository to your local machine:

   ```
   git clone <repository-url>
   cd custom-server-file-manager/server
   ```

2. **Create a Virtual Environment**

   It is recommended to create a virtual environment to manage dependencies:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Install the required Python packages using pip:

   ```
   pip install -r requirements.txt
   ```

4. **Configure Settings**

   Update the configuration settings in `src/config/settings.py` as needed. This may include database connections, API keys, and other environment variables.

5. **Run the Application**

   Start the server application by running:

   ```
   python src/app.py
   ```

   The server should now be running locally. You can access it at `http://localhost:5000` (or the port specified in your configuration).

## Deployment on Railway

To deploy the server application on Railway:

1. Ensure you have a `railway.json` file configured with your project settings.
2. Use the Railway CLI to deploy:

   ```
   railway up
   ```

3. Follow the prompts to complete the deployment process.

## Additional Information

For more details on the server's functionality and API endpoints, refer to the `README.md` file located in the `server` directory.