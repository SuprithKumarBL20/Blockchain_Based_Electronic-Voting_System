from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import json

from database.models import db, Voter, Candidate, Election, Vote, BlockchainBlock
from blockchain.blockchain import blockchain, VoteHasher

voter_bp = Blueprint('voter', __name__)

@voter_bp.route('/dashboard')
@login_required
def voter_dashboard():
    if not isinstance(current_user, Voter):
        return redirect(url_for('admin.admin_dashboard'))
    
    # Get current election
    current_election = Election.query.filter_by(is_active=True).first()
    
    # Check if voter has already voted in THIS election
    has_voted = False
    if current_election:
        vote = Vote.query.filter_by(voter_id=current_user.id, election_id=current_election.id).first()
        if vote:
            has_voted = True
    
    return render_template('voter_dashboard.html', 
                         voter=current_user,
                         election=current_election,
                         has_voted=has_voted)

@voter_bp.route('/vote')
@login_required
def vote_page():
    if not isinstance(current_user, Voter):
        return redirect(url_for('admin.admin_dashboard'))
    
    # Get current active election
    current_election = Election.query.filter_by(is_active=True).first()
    
    if not current_election:
        flash('No active election available for voting.', 'warning')
        return redirect(url_for('voter.voter_dashboard'))
    
    # Check if voter has already voted in THIS election
    existing_vote = Vote.query.filter_by(voter_id=current_user.id, election_id=current_election.id).first()
    if existing_vote:
        flash('You have already voted in this election.', 'warning')
        return redirect(url_for('voter.voter_dashboard'))
    
    # Check if election is currently active
    if not current_election.is_currently_active():
        flash('Voting is not currently open.', 'warning')
        return redirect(url_for('voter.voter_dashboard'))
    
    # Get all active candidates
    candidates = Candidate.query.filter_by(is_active=True).all()
    
    return render_template('vote.html', 
                         election=current_election,
                         candidates=candidates)

@voter_bp.route('/cast-vote', methods=['POST'])
@login_required
def cast_vote():
    if not isinstance(current_user, Voter):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        candidate_id = data.get('candidate_id')
        
        if not candidate_id:
            return jsonify({'error': 'Please select a candidate.'}), 400
        
        # Get current active election
        current_election = Election.query.filter_by(is_active=True).first()
        if not current_election or not current_election.is_currently_active():
            return jsonify({'error': 'Voting is not currently open.'}), 400
            
        # Check if voter has already voted in THIS election
        existing_vote = Vote.query.filter_by(voter_id=current_user.id, election_id=current_election.id).first()
        if existing_vote:
            return jsonify({'error': 'You have already voted in this election.'}), 400
        
        # Verify candidate exists and is active
        candidate = Candidate.query.filter_by(id=candidate_id, is_active=True).first()
        if not candidate:
            return jsonify({'error': 'Invalid candidate selected.'}), 400
        
        # Generate hashes for privacy
        voter_hash = VoteHasher.hash_voter_id(str(current_user.id))
        vote_hash = VoteHasher.hash_vote(
            str(current_user.id), 
            str(candidate_id), 
            datetime.utcnow()
        )
        
        # Add vote to blockchain directly via DB to ensure consistency
        block = blockchain.create_block_in_db(db.session, voter_hash, vote_hash)
        
        # Create vote record
        vote = Vote(
            voter_id=current_user.id,
            candidate_id=candidate_id,
            election_id=current_election.id,
            block_hash=block.current_hash,
            vote_hash=vote_hash,
            voter_hash=voter_hash
        )
        
        # Update voter status - keep has_voted as a general flag "has ever voted" if needed, 
        # but logic relies on Vote table now.
        current_user.has_voted = True
        current_user.voted_at = datetime.utcnow()
        
        # Save to database
        db.session.add(vote)
        db.session.commit()
        
        return jsonify({
            'message': 'Vote cast successfully!',
            'block_hash': block.current_hash,
            'block_index': block.index
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cast vote: {str(e)}'}), 500

@voter_bp.route('/voting-history')
@login_required
def voting_history():
    if not isinstance(current_user, Voter):
        return redirect(url_for('admin.admin_dashboard'))
    
    # Get voter's vote history
    votes = Vote.query.filter_by(voter_id=current_user.id).all()
    
    vote_history = []
    for vote in votes:
        vote_data = {
            'election_title': vote.election.title,
            'candidate_name': vote.candidate.name,
            'party_name': vote.candidate.party_name,
            'voted_at': vote.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'block_hash': vote.block_hash
        }
        vote_history.append(vote_data)
    
    return render_template('voting_history.html', vote_history=vote_history)

@voter_bp.route('/profile')
@login_required
def profile():
    if not isinstance(current_user, Voter):
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('voter_profile.html', voter=current_user)

@voter_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if not isinstance(current_user, Voter):
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update allowed fields
            if 'phone' in data:
                current_user.phone = data['phone']
            if 'email' in data:
                # Check if email is already taken by another user
                existing_voter = Voter.query.filter_by(email=data['email']).first()
                if existing_voter and existing_voter.id != current_user.id:
                    return jsonify({'error': 'Email already in use'}), 400
                current_user.email = data['email']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully!'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
    
    return render_template('edit_profile.html', voter=current_user)

@voter_bp.route('/api/election-status')
@login_required
def election_status():
    if not isinstance(current_user, Voter):
        return jsonify({'error': 'Unauthorized'}), 403
    
    current_election = Election.query.filter_by(is_active=True).first()
    
    if not current_election:
        return jsonify({
            'has_election': False,
            'has_voted': False
        })
    
    # Check if voter has voted in THIS election
    has_voted = False
    vote = Vote.query.filter_by(voter_id=current_user.id, election_id=current_election.id).first()
    if vote:
        has_voted = True
    
    return jsonify({
        'has_election': True,
        'election_title': current_election.title,
        'election_description': current_election.description,
        'is_active': current_election.is_currently_active(),
        'start_time': current_election.start_time.isoformat(),
        'end_time': current_election.end_time.isoformat(),
        'has_voted': has_voted
    })

@voter_bp.route('/api/candidates')
@login_required
def get_candidates():
    if not isinstance(current_user, Voter):
        return jsonify({'error': 'Unauthorized'}), 403
    
    candidates = Candidate.query.filter_by(is_active=True).all()
    
    candidates_data = []
    for candidate in candidates:
        candidate_data = {
            'id': candidate.id,
            'name': candidate.name,
            'party_name': candidate.party_name,
            'party_symbol': candidate.party_symbol,
            'description': candidate.description
        }
        candidates_data.append(candidate_data)
    
    return jsonify({'candidates': candidates_data})