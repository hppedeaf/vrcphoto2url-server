class DeleteWorker:
    """Worker for handling file deletions from the server."""
    
    def __init__(self, server_client):
        self.server_client = server_client

    def delete_file(self, file_id):
        """Delete a file from the server by its ID."""
        try:
            response = self.server_client.delete_file(file_id)
            if response.get('success'):
                print(f"File with ID {file_id} deleted successfully.")
            else:
                print(f"Failed to delete file with ID {file_id}: {response.get('error')}")
        except Exception as e:
            print(f"Error occurred while deleting file with ID {file_id}: {str(e)}")