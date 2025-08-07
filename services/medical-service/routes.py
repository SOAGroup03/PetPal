from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime
from models import MedicalModel
from functools import wraps

medical_bp = Blueprint('medical', __name__)
medical_model = MedicalModel()

def convert_dates_to_strings(record):
    """Convert datetime objects to ISO strings for JSON serialization"""
    date_fields = ['visit_date', 'created_at', 'updated_at', 'follow_up_date']
    for field in date_fields:
        if field in record and record[field]:
            if hasattr(record[field], 'isoformat'):
                record[field] = record[field].isoformat()
    return record

def verify_token(token):
    """Verify token with user service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(
            f"{os.getenv('USER_SERVICE_URL')}/api/users/verify-token",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def verify_pet_ownership(pet_id, token):
    """Verify pet ownership with pet service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{os.getenv('PET_SERVICE_URL')}/api/pets/verify/{pet_id}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_data = verify_token(token)
        if not user_data or not user_data.get('valid'):
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(user_data['user'], token, *args, **kwargs)
    return decorated

@medical_bp.route('/', methods=['POST'])
@token_required
def create_medical_record(current_user, token):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['pet_id', 'visit_date', 'record_type', 'veterinarian', 'diagnosis']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verify pet ownership
        pet_verification = verify_pet_ownership(data['pet_id'], token)
        if not pet_verification or not pet_verification.get('valid'):
            return jsonify({'message': 'Pet not found or access denied'}), 404
        
        # Parse visit date
        try:
            visit_date = datetime.fromisoformat(data['visit_date'].replace('Z', '+00:00'))
            data['visit_date'] = visit_date
        except:
            return jsonify({'message': 'Invalid visit date format'}), 400
        
        # Parse follow-up date if provided
        if data.get('follow_up_date'):
            try:
                follow_up_date = datetime.fromisoformat(data['follow_up_date'].replace('Z', '+00:00'))
                data['follow_up_date'] = follow_up_date
            except:
                return jsonify({'message': 'Invalid follow-up date format'}), 400
        
        # Convert numeric fields
        if data.get('weight'):
            try:
                data['weight'] = float(data['weight'])
            except (ValueError, TypeError):
                return jsonify({'message': 'Weight must be a number'}), 400
        
        if data.get('temperature'):
            try:
                data['temperature'] = float(data['temperature'])
            except (ValueError, TypeError):
                return jsonify({'message': 'Temperature must be a number'}), 400
        
        # Add user_id to medical data
        data['user_id'] = current_user['id']
        
        # Create medical record
        record_id = medical_model.create_medical_record(data)
        if record_id:
            return jsonify({
                'message': 'Medical record created successfully',
                'record_id': record_id
            }), 201
        else:
            return jsonify({'message': 'Failed to create medical record'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/', methods=['GET'])
@token_required
def get_medical_records(current_user, token):
    try:
        records = medical_model.get_medical_records_by_user(current_user['id'])
        
        # Convert datetime objects to ISO strings
        for record in records:
            convert_dates_to_strings(record)
        
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_records(current_user, token):
    try:
        limit = request.args.get('limit', 10, type=int)
        records = medical_model.get_recent_records(current_user['id'], limit)
        
        # Convert datetime objects to ISO strings
        for record in records:
            convert_dates_to_strings(record)
        
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/<record_id>', methods=['GET'])
@token_required
def get_medical_record(current_user, token, record_id):
    try:
        record = medical_model.get_medical_record_by_id_and_user(record_id, current_user['id'])
        if record:
            convert_dates_to_strings(record)
            return jsonify(record), 200
        else:
            return jsonify({'message': 'Medical record not found'}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/<record_id>', methods=['PUT'])
@token_required
def update_medical_record(current_user, token, record_id):
    try:
        # Verify record ownership
        record = medical_model.get_medical_record_by_id_and_user(record_id, current_user['id'])
        if not record:
            return jsonify({'message': 'Medical record not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Handle visit date update
        if 'visit_date' in data and data['visit_date']:
            try:
                visit_date = datetime.fromisoformat(data['visit_date'].replace('Z', '+00:00'))
                data['visit_date'] = visit_date
            except:
                return jsonify({'message': 'Invalid visit date format'}), 400
        
        # Handle follow-up date update
        if 'follow_up_date' in data and data['follow_up_date']:
            try:
                follow_up_date = datetime.fromisoformat(data['follow_up_date'].replace('Z', '+00:00'))
                data['follow_up_date'] = follow_up_date
            except:
                return jsonify({'message': 'Invalid follow-up date format'}), 400
        
        # Convert numeric fields
        if 'weight' in data and data['weight']:
            try:
                data['weight'] = float(data['weight'])
            except (ValueError, TypeError):
                return jsonify({'message': 'Weight must be a number'}), 400
        
        if 'temperature' in data and data['temperature']:
            try:
                data['temperature'] = float(data['temperature'])
            except (ValueError, TypeError):
                return jsonify({'message': 'Temperature must be a number'}), 400
        
        # Remove fields that shouldn't be updated
        forbidden_fields = ['_id', 'user_id', 'created_at']
        for field in forbidden_fields:
            data.pop(field, None)
        
        if medical_model.update_medical_record(record_id, data):
            return jsonify({'message': 'Medical record updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update medical record'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/<record_id>', methods=['DELETE'])
@token_required
def delete_medical_record(current_user, token, record_id):
    try:
        # Verify record ownership
        record = medical_model.get_medical_record_by_id_and_user(record_id, current_user['id'])
        if not record:
            return jsonify({'message': 'Medical record not found'}), 404
        
        if medical_model.delete_medical_record(record_id):
            return jsonify({'message': 'Medical record deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete medical record'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/pet/<pet_id>', methods=['GET'])
@token_required
def get_medical_records_by_pet(current_user, token, pet_id):
    try:
        # Verify pet ownership
        pet_verification = verify_pet_ownership(pet_id, token)
        if not pet_verification or not pet_verification.get('valid'):
            return jsonify({'message': 'Pet not found or access denied'}), 404
        
        records = medical_model.get_medical_records_by_pet(pet_id)
        
        # Convert datetime objects to ISO strings
        for record in records:
            if 'visit_date' in record:
                record['visit_date'] = record['visit_date'].isoformat()
            if 'created_at' in record:
                record['created_at'] = record['created_at'].isoformat()
            if 'updated_at' in record:
                record['updated_at'] = record['updated_at'].isoformat()
            if 'follow_up_date' in record and record['follow_up_date']:
                record['follow_up_date'] = record['follow_up_date'].isoformat()
        
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/pet/<pet_id>/vaccinations', methods=['GET'])
@token_required
def get_vaccination_history(current_user, token, pet_id):
    try:
        # Verify pet ownership
        pet_verification = verify_pet_ownership(pet_id, token)
        if not pet_verification or not pet_verification.get('valid'):
            return jsonify({'message': 'Pet not found or access denied'}), 404
        
        records = medical_model.get_vaccination_history(pet_id)
        
        # Convert datetime objects to ISO strings
        for record in records:
            if 'visit_date' in record:
                record['visit_date'] = record['visit_date'].isoformat()
            if 'created_at' in record:
                record['created_at'] = record['created_at'].isoformat()
            if 'updated_at' in record:
                record['updated_at'] = record['updated_at'].isoformat()
            if 'follow_up_date' in record and record['follow_up_date']:
                record['follow_up_date'] = record['follow_up_date'].isoformat()
        
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/pet/<pet_id>/type/<record_type>', methods=['GET'])
@token_required
def get_records_by_type(current_user, token, pet_id, record_type):
    try:
        # Verify pet ownership
        pet_verification = verify_pet_ownership(pet_id, token)
        if not pet_verification or not pet_verification.get('valid'):
            return jsonify({'message': 'Pet not found or access denied'}), 404
        
        records = medical_model.get_records_by_type(pet_id, record_type)
        
        # Convert datetime objects to ISO strings
        for record in records:
            if 'visit_date' in record:
                record['visit_date'] = record['visit_date'].isoformat()
            if 'created_at' in record:
                record['created_at'] = record['created_at'].isoformat()
            if 'updated_at' in record:
                record['updated_at'] = record['updated_at'].isoformat()
            if 'follow_up_date' in record and record['follow_up_date']:
                record['follow_up_date'] = record['follow_up_date'].isoformat()
        
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/stats', methods=['GET'])
@token_required
def get_medical_stats(current_user, token):
    try:
        records = medical_model.get_medical_records_by_user(current_user['id'])
        
        # Calculate statistics
        stats = {
            'total_records': len(records),
            'record_types': {},
            'recent_visits': 0,
            'upcoming_followups': 0
        }
        
        # Count by record type
        for record in records:
            record_type = record.get('record_type', 'other')
            stats['record_types'][record_type] = stats['record_types'].get(record_type, 0) + 1
        
        # Count recent visits (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        future_date = datetime.utcnow() + timedelta(days=30)
        
        for record in records:
            visit_date = record.get('visit_date')
            if visit_date and visit_date >= thirty_days_ago:
                stats['recent_visits'] += 1
            
            follow_up_date = record.get('follow_up_date')
            if follow_up_date and follow_up_date <= future_date and follow_up_date >= datetime.utcnow():
                stats['upcoming_followups'] += 1
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/search', methods=['GET'])
@token_required
def search_medical_records(current_user, token):
    try:
        # Get search parameters
        query = request.args.get('q', '')
        record_type = request.args.get('type', '')
        pet_id = request.args.get('pet_id', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Start with all user's records
        records = medical_model.get_medical_records_by_user(current_user['id'])
        
        # Apply filters
        if query:
            # Search in diagnosis, treatment, medications, and notes
            filtered_records = []
            query_lower = query.lower()
            for record in records:
                searchable_fields = [
                    record.get('diagnosis', ''),
                    record.get('treatment', ''),
                    record.get('medications', ''),
                    record.get('notes', ''),
                    record.get('veterinarian', '')
                ]
                if any(query_lower in field.lower() for field in searchable_fields if field):
                    filtered_records.append(record)
            records = filtered_records
        
        if record_type:
            records = [r for r in records if r.get('record_type') == record_type]
        
        if pet_id:
            records = [r for r in records if r.get('pet_id') == pet_id]
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                records = [r for r in records if r.get('visit_date') and r['visit_date'] >= start_dt]
            except:
                return jsonify({'message': 'Invalid start date format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                records = [r for r in records if r.get('visit_date') and r['visit_date'] <= end_dt]
            except:
                return jsonify({'message': 'Invalid end date format'}), 400
        
        # Convert datetime objects to ISO strings
        for record in records:
            if 'visit_date' in record:
                record['visit_date'] = record['visit_date'].isoformat()
            if 'created_at' in record:
                record['created_at'] = record['created_at'].isoformat()
            if 'updated_at' in record:
                record['updated_at'] = record['updated_at'].isoformat()
            if 'follow_up_date' in record and record['follow_up_date']:
                record['follow_up_date'] = record['follow_up_date'].isoformat()
        
        return jsonify({
            'records': records,
            'total': len(records),
            'query': query
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@medical_bp.route('/export', methods=['GET'])
@token_required
def export_medical_records(current_user, token):
    try:
        records = medical_model.get_medical_records_by_user(current_user['id'])
        
        # Convert datetime objects to ISO strings for export
        export_records = []
        for record in records:
            export_record = record.copy()
            if 'visit_date' in export_record:
                export_record['visit_date'] = export_record['visit_date'].isoformat()
            if 'created_at' in export_record:
                export_record['created_at'] = export_record['created_at'].isoformat()
            if 'updated_at' in export_record:
                export_record['updated_at'] = export_record['updated_at'].isoformat()
            if 'follow_up_date' in export_record and export_record['follow_up_date']:
                export_record['follow_up_date'] = export_record['follow_up_date'].isoformat()
            export_records.append(export_record)
        
        return jsonify({
            'records': export_records,
            'exported_at': datetime.utcnow().isoformat(),
            'total_records': len(export_records)
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500