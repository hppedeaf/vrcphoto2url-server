# API Documentation for Custom Server File Manager

## Overview

This document provides an overview of the API endpoints available in the Custom Server File Manager application. The API allows clients to interact with the server for file management operations, including uploading, retrieving, and deleting files.

## Base URL

The base URL for the API is:

```
http://<your-server-url>/api
```

## Authentication

Most endpoints require authentication. Clients must include a valid token in the `Authorization` header of their requests.

### Example Header

```
Authorization: Bearer <your-token>
```

## Endpoints

### 1. Upload File

- **POST** `/upload`
- **Description**: Uploads a new file to the server.
- **Request Body**: 
  - `file`: The file to be uploaded (form-data).
- **Response**:
  - **200 OK**: Returns the details of the uploaded file.
  - **400 Bad Request**: If the file is invalid or missing.

### 2. List Files

- **GET** `/files`
- **Description**: Retrieves a list of all files stored on the server.
- **Response**:
  - **200 OK**: Returns a list of files with their metadata.
  - **401 Unauthorized**: If the user is not authenticated.

### 3. Get File Details

- **GET** `/files/{file_id}`
- **Description**: Retrieves details of a specific file.
- **Parameters**:
  - `file_id`: The ID of the file to retrieve.
- **Response**:
  - **200 OK**: Returns the file details.
  - **404 Not Found**: If the file does not exist.

### 4. Delete File

- **DELETE** `/files/{file_id}`
- **Description**: Deletes a specific file from the server.
- **Parameters**:
  - `file_id`: The ID of the file to delete.
- **Response**:
  - **204 No Content**: If the file was successfully deleted.
  - **404 Not Found**: If the file does not exist.
  - **401 Unauthorized**: If the user is not authenticated.

## Error Handling

All responses will include an error message in the body if an error occurs. The format will be:

```json
{
  "error": "Error message here"
}
```

## Conclusion

This API documentation provides a comprehensive guide to the available endpoints for the Custom Server File Manager. For further assistance, please refer to the server's README or contact the development team.