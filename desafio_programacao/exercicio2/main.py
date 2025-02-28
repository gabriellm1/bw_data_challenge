import io
from io import TextIOWrapper

def chunk_string(text, chunk_size):
    """
    Helper function to yield string chunks in reverse order with UTF-8
    
    Args:
        text: The string to chunk
        chunk_size: The size of the chunks
    Returns:
        An iterator of chunks
    """
    # Convert to bytes and get total length
    encoded = text.encode('utf-8')
    total_length = len(encoded)
    chunks = []
    pos = 0
    
    while pos < total_length:
        # Calculate end position for this chunk
        end = pos + chunk_size
        
        if end < total_length:
            # Adjust end to not break UTF-8 character
            while end > pos and (encoded[end] & 0xC0) == 0x80:
                end -= 1
        else:
            end = total_length
            
        # Extract and decode chunk
        chunk = encoded[pos:end].decode('utf-8')
        chunks.append(chunk)
        pos = end
    
    # Return chunks in reverse order
    return reversed(chunks)

def last_lines(filename, buffer_size = io.DEFAULT_BUFFER_SIZE):
    """
    Implements Linux tac command functionality with UTF-8 safety
    
    Args:
        filename: The file to read in reverse
        buffer_size: The buffer size to use
    Returns:
        An iterator of lines in reverse order    
    """
    with open(filename, 'rb') as binary_file:
        binary_file.seek(0, 2)
        file_size = binary_file.tell()

        if file_size == 0:
            return

        position = file_size
        remaining = b''
        
        while position > 0:
            read_size = min(buffer_size, position)
            position -= read_size
            
            binary_file.seek(position)
            chunk = binary_file.read(read_size)
            full_chunk = chunk + remaining
            
            try:
                text = full_chunk.decode('utf-8')
                text = text.replace('\\n', '\n')
                lines = text.splitlines(keepends=True)
                
                if position > 0:
                    remaining = chunk[:chunk.rfind(b'\n')+1] if b'\n' in chunk else chunk
                    lines = lines[1:]
                else:
                    remaining = b''
                
                for line in reversed(lines):
                    if len(line.encode('utf-8')) > buffer_size:
                        for chunk in chunk_string(line, buffer_size):
                            yield chunk
                    else:
                        yield line
                    
            except UnicodeDecodeError:
                if position > 0:
                    position += 1
                    remaining = full_chunk
                else:
                    text = full_chunk.decode('utf-8', errors='replace')
                    for line in reversed(text.splitlines(keepends=True)):
                        if len(line.encode('utf-8')) > buffer_size:
                            for chunk in chunk_string(line, buffer_size):
                                yield chunk
                        else:
                            yield line