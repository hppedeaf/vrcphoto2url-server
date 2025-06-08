from flask import Blueprint, jsonify, request
from ..models.file_model import FileModel
from ..services.file_service import FileService

files_bp = Blueprint('files', __name__)
file_service = FileService()

@files_bp.route('/files', methods=['GET'])
def list_files():
    files = file_service.get_all_files()
    return jsonify(files), 200

@files_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    file = file_service.get_file_by_id(file_id)
    if file:
        return jsonify(file), 200
    return jsonify({'error': 'File not found'}), 404

@files_bp.route('/files', methods=['DELETE'])
def delete_file():
    file_id = request.json.get('file_id')
    if file_service.delete_file(file_id):
        return jsonify({'message': 'File deleted successfully'}), 200
    return jsonify({'error': 'File not found or could not be deleted'}), 404