from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from datetime import datetime
import json
import io
from flask import Response
import os
from werkzeug.utils import secure_filename

from database.models import db, Voter, Candidate, Election, Vote, BlockchainBlock, Admin
from blockchain.blockchain import blockchain

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics
    total_voters = Voter.query.count()
    approved_voters = Voter.query.filter_by(is_approved=True).count()
    pending_voters = Voter.query.filter_by(is_approved=False).count()
    total_votes = Vote.query.count()
    
    # Get current election
    current_election = Election.query.filter_by(is_active=True).first()
    
    # Get blockchain info
    blockchain_info = {
        'chain_length': blockchain.get_chain_length(),
        'is_valid': blockchain.is_chain_valid()
    }
    
    return render_template('admin_dashboard.html',
                         stats={
                             'total_voters': total_voters,
                             'approved_voters': approved_voters,
                             'pending_voters': pending_voters,
                             'total_votes': total_votes
                         },
                         election=current_election,
                         blockchain=blockchain_info)

@admin_bp.route('/voters')
@login_required
@admin_required
def manage_voters():
    voters = Voter.query.order_by(Voter.created_at.desc()).all()
    return render_template('admin_voters.html', voters=voters)

@admin_bp.route('/voters/<int:voter_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_voter(voter_id):
    try:
        voter = Voter.query.get_or_404(voter_id)
        
        if voter.is_approved:
            return jsonify({'error': 'Voter already approved'}), 400
        
        voter.is_approved = True
        voter.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Voter approved successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to approve voter: {str(e)}'}), 500

@admin_bp.route('/voters/<int:voter_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_voter(voter_id):
    try:
        voter = Voter.query.get_or_404(voter_id)
        
        if voter.is_approved:
            return jsonify({'error': 'Cannot reject approved voter'}), 400
        
        # Instead of deleting, we can deactivate the voter
        voter.is_active = False
        voter.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Voter rejected successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reject voter: {str(e)}'}), 500

@admin_bp.route('/voters/<int:voter_id>/block', methods=['POST'])
@login_required
@admin_required
def block_voter(voter_id):
    try:
        voter = Voter.query.get_or_404(voter_id)
        
        if not voter.is_active:
            return jsonify({'error': 'Voter already blocked'}), 400
        
        voter.is_active = False
        voter.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Voter blocked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to block voter: {str(e)}'}), 500

@admin_bp.route('/voters/<int:voter_id>/unblock', methods=['POST'])
@login_required
@admin_required
def unblock_voter(voter_id):
    try:
        voter = Voter.query.get_or_404(voter_id)
        
        if voter.is_active:
            return jsonify({'error': 'Voter already active'}), 400
        
        voter.is_active = True
        voter.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Voter unblocked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to unblock voter: {str(e)}'}), 500

@admin_bp.route('/voters/<int:voter_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_voter(voter_id):
    try:
        voter = Voter.query.get_or_404(voter_id)
        
        # Check if voter has already voted
        if voter.has_voted:
            return jsonify({'error': 'Cannot remove voter who has already voted'}), 400
        
        # Delete the voter
        db.session.delete(voter)
        db.session.commit()
        
        return jsonify({'message': 'Voter removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove voter: {str(e)}'}), 500

@admin_bp.route('/voters/<int:voter_id>/details')
@login_required
@admin_required
def voter_details(voter_id):
    try:
        voter = Voter.query.get_or_404(voter_id)
        
        # Get voting history
        votes = Vote.query.filter_by(voter_id=voter_id).all()
        
        return render_template('admin_voter_details.html', 
                             voter=voter, 
                             votes=votes)
        
    except Exception as e:
        return jsonify({'error': f'Failed to load voter details: {str(e)}'}), 500

@admin_bp.route('/candidates')
@login_required
@admin_required
def manage_candidates():
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template('admin_candidates.html', candidates=candidates)

@admin_bp.route('/candidates/add', methods=['POST'])
@login_required
@admin_required
def add_candidate():
    try:
        # Accept multipart form data for optional symbol upload
        name = request.form.get('name')
        party_name = request.form.get('party_name')
        description = request.form.get('description', '')
        symbol_file = request.files.get('party_symbol')

        if not name or not party_name:
            return jsonify({'error': 'name and party_name are required', 'success': False}), 400

        party_symbol_filename = None
        if symbol_file and symbol_file.filename:
            uploads_dir = os.path.join('static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(symbol_file.filename)
            file_path = os.path.join(uploads_dir, filename)
            symbol_file.save(file_path)
            party_symbol_filename = filename

        candidate = Candidate(
            name=name,
            party_name=party_name,
            description=description,
            party_symbol=party_symbol_filename
        )

        db.session.add(candidate)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Candidate added successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add candidate: {str(e)}', 'success': False}), 500

@admin_bp.route('/candidates/<int:candidate_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_candidate(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)
        candidate.is_active = not candidate.is_active
        
        db.session.commit()
        
        status = 'activated' if candidate.is_active else 'deactivated'
        return jsonify({'success': True, 'message': f'Candidate {status} successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to toggle candidate: {str(e)}', 'success': False}), 500

@admin_bp.route('/candidates/<int:candidate_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_candidate(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)
        
        # Check if candidate can be removed (allow removal of any candidate with proper warning)
        if candidate.is_active:
            # Auto-deactivate before removal
            candidate.is_active = False
            db.session.commit()
        
        # Check if there are any votes for this candidate
        vote_count = Vote.query.filter_by(candidate_id=candidate_id).count()
        if vote_count > 0:
            return jsonify({'error': 'Cannot remove candidate with existing votes', 'success': False}), 400
        
        # Remove the candidate
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Candidate removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove candidate: {str(e)}', 'success': False}), 500

@admin_bp.route('/elections')
@login_required
@admin_required
def manage_elections():
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('admin_elections.html', elections=elections)

@admin_bp.route('/elections/create', methods=['POST'])
@login_required
@admin_required
def create_election():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse datetime
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        if start_time >= end_time:
            return jsonify({'error': 'End time must be after start time'}), 400
        
        # Deactivate any existing active election
        Election.query.filter_by(is_active=True).update({'is_active': False})
        
        # Create new election
        election = Election(
            title=data['title'],
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        
        db.session.add(election)
        db.session.commit()
        
        return jsonify({'message': 'Election created successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create election: {str(e)}'}), 500

@admin_bp.route('/elections/<int:election_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_election(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        
        # If publishing, allow it even if election is not over
        if not election.is_published:
            # Publish the election results
            election.is_published = True
            status = 'published'
            message = 'Election results published successfully'
        else:
            # Unpublish the election results
            election.is_published = False
            status = 'unpublished'
            message = 'Election results unpublished successfully'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to toggle election: {str(e)}'}), 500

@admin_bp.route('/elections/<int:election_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_election(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        
        if election.is_currently_active():
            return jsonify({'error': 'Cannot remove currently active election', 'success': False}), 400
        
        # Check if there are any votes associated with this election
        vote_count = Vote.query.filter_by(election_id=election_id).count()
        if vote_count > 0:
            return jsonify({'error': 'Cannot remove election with existing votes', 'success': False}), 400
        
        # Remove the election
        db.session.delete(election)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Election removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to deactivate election: {str(e)}', 'success': False}), 500

@admin_bp.route('/election/publish/<int:election_id>', methods=['POST'])
@login_required
@admin_required
def publish_election_results(election_id):
    """Publish election results"""
    try:
        election = Election.query.get_or_404(election_id)
        
        # Mark election as published
        election.is_published = True
        election.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Election results published successfully!', 'success')
        return jsonify({'success': True, 'message': 'Results published successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to publish results: {str(e)}'}), 500

@admin_bp.route('/elections/<int:election_id>/overview')
@login_required
@admin_required
def election_overview(election_id):
    """View detailed election overview"""
    election = Election.query.get_or_404(election_id)
    
    # Get candidates for this election
    candidates = Candidate.query.filter_by(is_active=True).all()
    
    # Get vote counts for each candidate
    candidate_results = []
    total_votes = 0
    
    for candidate in candidates:
        vote_count = Vote.query.filter_by(
            candidate_id=candidate.id,
            election_id=election_id
        ).count()
        
        candidate_results.append({
            'candidate': candidate,
            'vote_count': vote_count
        })
        total_votes += vote_count
    
    # Calculate percentages
    if total_votes > 0:
        for result in candidate_results:
            result['percentage'] = round((result['vote_count'] / total_votes) * 100, 2)
    
    # Sort by vote count
    candidate_results.sort(key=lambda x: x['vote_count'], reverse=True)
    
    return render_template('admin_election_overview.html',
                         election=election,
                         candidate_results=candidate_results,
                         total_votes=total_votes)

@admin_bp.route('/elections/<int:election_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_election(election_id):
    """Edit election details"""
    election = Election.query.get_or_404(election_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['title', 'start_time', 'end_time']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Parse datetime
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            
            if start_time >= end_time:
                return jsonify({'error': 'End time must be after start time'}), 400
            
            # Update election
            election.title = data['title']
            election.description = data.get('description', '')
            election.start_time = start_time
            election.end_time = end_time
            election.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({'message': 'Election updated successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update election: {str(e)}'}), 500
    
    # GET request - return election data
    return jsonify({
        'id': election.id,
        'title': election.title,
        'description': election.description,
        'start_time': election.start_time.isoformat(),
        'end_time': election.end_time.isoformat(),
        'is_active': election.is_active,
        'is_published': election.is_published
    })

@admin_bp.route('/blockchain')
@login_required
@admin_required
def view_blockchain():
    # Get all blocks from database
    blocks = BlockchainBlock.query.order_by(BlockchainBlock.block_index).all()
    
    # Enhance blocks with vote information
    enhanced_blocks = []
    for block in blocks:
        # Find the vote associated with this block
        vote = Vote.query.filter_by(block_hash=block.current_hash).first()
        
        # Create enhanced block data
        enhanced_block = {
            'block_index': block.block_index,
            'timestamp': block.timestamp,
            'voter_hash': block.voter_hash,
            'vote_hash': block.vote_hash,
            'previous_hash': block.previous_hash,
            'current_hash': block.current_hash,
            'nonce': block.nonce,
            'vote_data': None
        }
        
        if vote:
            enhanced_block['vote_data'] = {
                'voter_id': vote.virtual_voter_id if hasattr(vote, 'virtual_voter_id') else vote.voter_hash[:8],
                'candidate_name': vote.candidate.name,
                'candidate_party': vote.candidate.party_name,
                'election_title': vote.election.title,
                'vote_timestamp': vote.created_at
            }
        
        enhanced_blocks.append(enhanced_block)
    
    return render_template('admin_blockchain.html', blocks=enhanced_blocks)

# New routes to match frontend actions
@admin_bp.route('/elections/<int:election_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_election(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        if not election.is_active:
            return jsonify({'error': 'Election already inactive', 'success': False}), 400
        election.is_active = False
        election.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Election deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to deactivate election: {str(e)}', 'success': False}), 500

@admin_bp.route('/election/end/<int:election_id>', methods=['POST'])
@login_required
@admin_required
def end_election_now(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        election.end_time = datetime.utcnow()
        election.is_active = False
        election.is_published = True
        election.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Election ended and results published'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to end election: {str(e)}', 'success': False}), 500

@admin_bp.route('/results')
@login_required
@admin_required
def view_results():
    try:
        # Current active election
        current_election = Election.query.filter_by(is_active=True).first()
        current_results = []
        current_total_votes = 0

        if current_election:
            candidates = Candidate.query.all()
            # Count votes per candidate for the current election
            for candidate in candidates:
                vote_count = Vote.query.filter_by(candidate_id=candidate.id, election_id=current_election.id).count()
                current_total_votes += vote_count
                current_results.append({
                    'candidate': candidate,
                    'vote_count': vote_count
                })
            # Calculate percentages
            if current_total_votes > 0:
                for result in current_results:
                    result['percentage'] = round((result['vote_count'] / current_total_votes) * 100, 2)
            else:
                for result in current_results:
                    result['percentage'] = 0

        # Historical results for completed and published elections
        historical_results = []
        past_elections = Election.query.filter_by(is_active=False, is_published=True).order_by(Election.end_time.desc()).all()
        for election in past_elections:
            # Compute results per election
            election_total = 0
            cand_results = []
            candidates = Candidate.query.all()
            for candidate in candidates:
                vote_count = Vote.query.filter_by(candidate_id=candidate.id, election_id=election.id).count()
                election_total += vote_count
                cand_results.append({
                    'candidate': candidate,
                    'vote_count': vote_count
                })
            # Percentages
            if election_total > 0:
                for r in cand_results:
                    r['percentage'] = round((r['vote_count'] / election_total) * 100, 2)
            else:
                for r in cand_results:
                    r['percentage'] = 0

            historical_results.append({
                'title': election.title,
                'end_time': election.end_time,
                'results': cand_results,
                'total_votes': election_total
            })

        return render_template('admin_results.html',
                               current_election=current_election,
                               current_results=current_results,
                               current_total_votes=current_total_votes,
                               historical_results=historical_results)
    except Exception as e:
        return jsonify({'error': f'Failed to load results: {str(e)}'}), 500

@admin_bp.route('/blockchain/download')
@login_required
@admin_required
def download_blockchain():
    try:
        # Get blockchain data
        blockchain_data = blockchain.to_dict()
        
        # Convert to JSON
        json_data = json.dumps(blockchain_data, indent=2)
        
        # Create response
        response = Response(
            json_data,
            mimetype='application/json',
            headers={
                'Content-Disposition': 'attachment; filename=blockchain.json'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Failed to download blockchain: {str(e)}'}), 500