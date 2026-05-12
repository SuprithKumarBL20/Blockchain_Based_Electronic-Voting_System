from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from database.models import db, Election, Candidate, Vote
from blockchain.blockchain import blockchain

election_bp = Blueprint('election', __name__)

@election_bp.route('/current')
@login_required
def current_election():
    """Get current active election information"""
    current_election = Election.query.filter_by(is_active=True).first()
    
    if not current_election:
        return jsonify({'has_election': False}), 200
    
    return jsonify({
        'has_election': True,
        'election': {
            'id': current_election.id,
            'title': current_election.title,
            'description': current_election.description,
            'start_time': current_election.start_time.isoformat(),
            'end_time': current_election.end_time.isoformat(),
            'is_active': current_election.is_active,
            'is_published': current_election.is_published,
            'is_currently_active': current_election.is_currently_active()
        }
    }), 200

@election_bp.route('/candidates')
@login_required
def election_candidates():
    """Get candidates for current election"""
    current_election = Election.query.filter_by(is_active=True).first()
    
    if not current_election:
        return jsonify({'error': 'No active election found'}), 404
    
    candidates = Candidate.query.filter_by(is_active=True).all()
    
    candidates_data = []
    for candidate in candidates:
        candidates_data.append({
            'id': candidate.id,
            'name': candidate.name,
            'party_name': candidate.party_name,
            'party_symbol': candidate.party_symbol,
            'description': candidate.description,
            'vote_count': candidate.get_vote_count()
        })
    
    return jsonify({'candidates': candidates_data}), 200

@election_bp.route('/results')
@login_required
def election_results():
    """Get election results"""
    current_election = Election.query.filter_by(is_active=True).first()
    
    if not current_election:
        return jsonify({'error': 'No active election found'}), 404
    
    if not current_election.is_published:
        return jsonify({'error': 'Election results not published yet'}), 403
    
    candidates = Candidate.query.filter_by(is_active=True).all()
    
    results = []
    total_votes = 0
    
    for candidate in candidates:
        vote_count = Vote.query.filter_by(
            candidate_id=candidate.id,
            election_id=current_election.id
        ).count()
        
        results.append({
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'party_name': candidate.party_name,
            'vote_count': vote_count
        })
        
        total_votes += vote_count
    
    # Calculate percentages
    for result in results:
        if total_votes > 0:
            result['percentage'] = round((result['vote_count'] / total_votes) * 100, 2)
        else:
            result['percentage'] = 0
    
    # Sort by vote count (descending)
    results.sort(key=lambda x: x['vote_count'], reverse=True)
    
    return jsonify({
        'election_title': current_election.title,
        'total_votes': total_votes,
        'results': results,
        'blockchain_valid': blockchain.is_chain_valid()
    }), 200