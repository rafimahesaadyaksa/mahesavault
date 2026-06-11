"""
Playfair Cipher Module — MahesaVault
Classical cipher using 5×5 key matrix and digraph substitution.

Rules:
    1. Create 5×5 matrix from key (I/J combined)
    2. Split plaintext into digraphs (pairs of 2 letters)
    3. If pair has same letters, insert 'X' between them
    4. Apply rules: same row → shift right, same column → shift down,
       rectangle → swap columns
"""


def _create_matrix(key: str) -> list:
    """
    Create the 5×5 Playfair cipher matrix from the key.
    
    The matrix is filled with the key characters first (no duplicates),
    then remaining alphabet letters. I and J share the same cell.
    
    Args:
        key: The keyword for matrix construction.
    
    Returns:
        5×5 matrix as a list of 5 lists, each containing 5 characters.
    """
    key = key.upper().replace('J', 'I')
    # Build ordered unique character list from key + remaining alphabet
    seen = set()
    matrix_chars = []
    
    for char in key:
        if char.isalpha() and char not in seen:
            seen.add(char)
            matrix_chars.append(char)
    
    for char in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':  # No J
        if char not in seen:
            seen.add(char)
            matrix_chars.append(char)
    
    # Reshape into 5×5 matrix
    matrix = [matrix_chars[i:i+5] for i in range(0, 25, 5)]
    return matrix


def _find_position(matrix: list, char: str) -> tuple:
    """Find the (row, col) position of a character in the matrix."""
    char = char.upper().replace('J', 'I')
    for row in range(5):
        for col in range(5):
            if matrix[row][col] == char:
                return (row, col)
    return None


def _prepare_text(text: str) -> str:
    """
    Prepare plaintext for Playfair encryption.
    
    - Convert to uppercase, remove non-alpha, replace J with I
    - Split into digraphs; if same letter pair, insert X
    - If odd length, pad with X
    """
    text = text.upper().replace('J', 'I')
    text = ''.join(c for c in text if c.isalpha())
    
    prepared = ''
    i = 0
    while i < len(text):
        prepared += text[i]
        if i + 1 < len(text):
            if text[i] == text[i + 1]:
                prepared += 'X'  # Insert filler between repeated letters
                i += 1
            else:
                prepared += text[i + 1]
                i += 2
        else:
            prepared += 'X'  # Pad odd-length text
            i += 1
    
    return prepared


def encrypt(plaintext: str, key: str) -> str:
    """
    Encrypt plaintext using Playfair cipher.
    
    Args:
        plaintext: The message to encrypt.
        key: The keyword for matrix construction.
    
    Returns:
        Encrypted ciphertext string.
    
    Raises:
        ValueError: If key is empty.
    """
    if not key:
        raise ValueError("Key must not be empty")
    
    matrix = _create_matrix(key)
    prepared = _prepare_text(plaintext)
    result = []
    
    # Process each digraph (pair of letters)
    for i in range(0, len(prepared), 2):
        r1, c1 = _find_position(matrix, prepared[i])
        r2, c2 = _find_position(matrix, prepared[i + 1])
        
        if r1 == r2:
            # Same row → shift right (wrap around)
            result.append(matrix[r1][(c1 + 1) % 5])
            result.append(matrix[r2][(c2 + 1) % 5])
        elif c1 == c2:
            # Same column → shift down (wrap around)
            result.append(matrix[(r1 + 1) % 5][c1])
            result.append(matrix[(r2 + 1) % 5][c2])
        else:
            # Rectangle → swap columns
            result.append(matrix[r1][c2])
            result.append(matrix[r2][c1])
    
    return ''.join(result)


def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt ciphertext using Playfair cipher.
    
    Args:
        ciphertext: The encrypted message.
        key: The keyword (same as used for encryption).
    
    Returns:
        Decrypted plaintext string.
    """
    if not key:
        raise ValueError("Key must not be empty")
    
    matrix = _create_matrix(key)
    ciphertext = ciphertext.upper().replace('J', 'I')
    ciphertext = ''.join(c for c in ciphertext if c.isalpha())
    result = []
    
    for i in range(0, len(ciphertext), 2):
        if i + 1 >= len(ciphertext):
            result.append(ciphertext[i])
            break
        
        r1, c1 = _find_position(matrix, ciphertext[i])
        r2, c2 = _find_position(matrix, ciphertext[i + 1])
        
        if r1 == r2:
            # Same row → shift left (reverse of encrypt)
            result.append(matrix[r1][(c1 - 1) % 5])
            result.append(matrix[r2][(c2 - 1) % 5])
        elif c1 == c2:
            # Same column → shift up (reverse of encrypt)
            result.append(matrix[(r1 - 1) % 5][c1])
            result.append(matrix[(r2 - 1) % 5][c2])
        else:
            # Rectangle → swap columns (same as encrypt)
            result.append(matrix[r1][c2])
            result.append(matrix[r2][c1])
    
    return ''.join(result)


def show_steps(plaintext: str, key: str) -> str:
    """Show the Playfair matrix and digraph processing steps."""
    matrix = _create_matrix(key)
    prepared = _prepare_text(plaintext)
    
    lines = []
    lines.append(f"**Playfair Cipher — Key = \"{key.upper()}\"**\n")
    
    # Show 5×5 matrix
    lines.append("**5×5 Key Matrix:**\n")
    lines.append("| | C1 | C2 | C3 | C4 | C5 |")
    lines.append("|---|---|---|---|---|---|")
    for i, row in enumerate(matrix):
        lines.append(f"| R{i+1} | {'|'.join(f' {c} ' for c in row)} |")
    
    lines.append(f"\n**Prepared text:** `{prepared}`")
    lines.append(f"\n**Digraph processing:**\n")
    lines.append("| Digraph | Pos1 | Pos2 | Rule | Result |")
    lines.append("|---------|------|------|------|--------|")
    
    result_chars = []
    for i in range(0, len(prepared), 2):
        pair = prepared[i:i+2]
        r1, c1 = _find_position(matrix, pair[0])
        r2, c2 = _find_position(matrix, pair[1])
        
        if r1 == r2:
            rule = "Same Row→Right"
            e1 = matrix[r1][(c1+1)%5]
            e2 = matrix[r2][(c2+1)%5]
        elif c1 == c2:
            rule = "Same Col→Down"
            e1 = matrix[(r1+1)%5][c1]
            e2 = matrix[(r2+1)%5][c2]
        else:
            rule = "Rectangle→Swap"
            e1 = matrix[r1][c2]
            e2 = matrix[r2][c1]
        
        result_chars.extend([e1, e2])
        lines.append(f"| {pair} | ({r1},{c1}) | ({r2},{c2}) | {rule} | {e1}{e2} |")
    
    lines.append(f"\n**Ciphertext:** `{''.join(result_chars)}`")
    return '\n'.join(lines)
