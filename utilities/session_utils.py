from flask import session

def get_current_user_id():
    """
    Get the current user ID from session in a consistent way.
    
    Returns:
        int: User ID if logged in, None otherwise
    """
    if 'user' not in session:
        return None
        
    # Try both common formats
    user = session['user']
    user_id = user.get('user_id') or user.get('id')
    
    return user_id

def get_current_username():
    """
    Get the current username from session.
    
    Returns:
        str: Username if logged in, None otherwise
    """
    if 'user' not in session:
        return None
        
    return session['user'].get('username')

def is_user_logged_in():
    """
    Check if a user is currently logged in.
    
    Returns:
        bool: True if logged in, False otherwise
    """
    return 'user' in session and get_current_user_id() is not None

def get_user_role():
    """
    Get the current user's role from session.
    
    Returns:
        str: Role if available, None otherwise
    """
    if 'user' not in session:
        return None
        
    return session['user'].get('role')