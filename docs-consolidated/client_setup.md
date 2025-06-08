# Client Setup Instructions

## Prerequisites

Before setting up the client application, ensure you have the following installed:

- Python 3.6 or higher
- pip (Python package installer)

## Installation Steps

1. **Clone the Repository**

   Start by cloning the repository to your local machine:

   ```
   git clone <repository-url>
   cd custom-server-file-manager
   ```

2. **Navigate to the Client Directory**

   Change to the client directory:

   ```
   cd client
   ```

3. **Install Dependencies**

   Install the required Python packages using pip:

   ```
   pip install -r requirements.txt
   ```

4. **Configure Server Connection**

   Open the `src/custom_server_dialog.py` file to configure the server connection settings. Update the server URL and any necessary authentication details.

5. **Run the Client Application**

   You can start the client application by running the following command:

   ```
   python src/custom_main.py
   ```

6. **Using the Application**

   - Upon launching, you will see the main window.
   - Use the settings dialog to configure auto-upload and other preferences.
   - Connect to the server using the connection dialog.

## Troubleshooting

- If you encounter issues connecting to the server, ensure that the server is running and accessible.
- Check the console for any error messages that may provide clues to the problem.

## Additional Resources

For more information on using the client application, refer to the `README.md` file located in the `client` directory.