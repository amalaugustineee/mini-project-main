from flask import Blueprint, render_template
from app.blockchain.blockchain import get_blockchain
from app.models.charity import Charity

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/blockchain')
def blockchain_explorer():
    blockchain = get_blockchain()
    
    # Prepare block data for display
    blocks = []
    for block in blockchain.chain:
        block_data = block.to_dict()
        # Get charity names for better UI display
        for tx in block_data['transactions']:
            if tx['transaction_type'] == 'donation':
                # For donation transactions, look up charity name
                charity = Charity.query.filter_by(blockchain_address=tx['recipient_id']).first()
                if charity:
                    tx['recipient_name'] = charity.name
                    
            if tx['transaction_type'] == 'spending':
                # For spending transactions, look up charity name
                charity = Charity.query.filter_by(blockchain_address=tx['sender_id']).first()
                if charity:
                    tx['sender_name'] = charity.name
        
        blocks.append(block_data)
        
    return render_template('blockchain.html', blocks=blocks) 