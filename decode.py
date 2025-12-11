from PIL import Image
import numpy as np
import os

BLOCK = 8
THRESHOLD = 0.40
MAGIC = b"BPCS"

# --- reuse your block complexity & segmentation functions ---
def block_complexity(block):
    transitions = 0
    for r in range(BLOCK):
        for c in range(BLOCK - 1):
            if block[r][c] != block[r][c+1]:
                transitions += 1
    for c in range(BLOCK):
        for r in range(BLOCK - 1):
            if block[r][c] != block[r+1][c]:
                transitions += 1
    max_transitions = (BLOCK * (BLOCK - 1)) * 2
    return transitions / max_transitions

def segment_bitplane(bitplane, block_size=BLOCK, threshold=THRESHOLD):
    h, w = bitplane.shape
    noise_positions = []
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = bitplane[i:i+block_size, j:j+block_size]
            if block.shape != (block_size, block_size):
                continue
            if block_complexity(block) >= threshold:
                noise_positions.append((i, j))
    return noise_positions

def int2bitarray(img_array):
    h, w = img_array.shape
    arr = np.empty((h, w), dtype=object)
    for i in range(h):
        for j in range(w):
            arr[i, j] = format(int(img_array[i, j]), '08b')
    return arr

# -------------------------
# Robust decoder
# -------------------------
def decode(stego_image_path, undo_flips=True, verbose=False):
    """
    Robust decoder:
      - undo_flips: if True, will reverse fliplr+flipud done by encoder
      - verbose: prints progress info
    """
    img = Image.open(stego_image_path).convert('RGB')
    r_arr, g_arr, b_arr = np.array(img.split()[0]), np.array(img.split()[1]), np.array(img.split()[2])
    h, w = r_arr.shape

    # If encoder flipped before saving (flipud(fliplr)), undo that here:
    if undo_flips:
        if verbose: print("[*] Undoing encoder flips (fliplr then flipud).")
        r_arr = np.flipud(np.fliplr(r_arr))
        g_arr = np.flipud(np.fliplr(g_arr))
        b_arr = np.flipud(np.fliplr(b_arr))

    channels = [('R', r_arr), ('G', g_arr), ('B', b_arr)]

    # Extract noise-like 8x8 blocks in the same order encoder used:
    # For each channel (R,G,B), for plane k=0..7 (MSB->LSB), left-to-right, top-to-bottom blocks
    collected_blocks = []  # each entry is 64-bit string

    for ch_name, ch_array in channels:
        bits_arr = int2bitarray(ch_array)  # array of 8-bit strings per pixel
        for k in range(8):  # MSB -> LSB (same as encoder)
            # Build plane
            plane = np.zeros((h, w), dtype=np.uint8)
            for i in range(h):
                for j in range(w):
                    plane[i, j] = int(bits_arr[i, j][k])  # '0' or '1'

            # get noise block positions in deterministic order
            noise_positions = segment_bitplane(plane, block_size=BLOCK, threshold=THRESHOLD)

            if verbose:
                print(f"  {ch_name}-channel plane {7-k}: found {len(noise_positions)} noise blocks")

            # Extract each block's 64 bits and append to list
            for (bi, bj) in noise_positions:
                block = plane[bi:bi+BLOCK, bj:bj+BLOCK]
                bstr = ''.join(str(int(block[r, c])) for r in range(BLOCK) for c in range(BLOCK))
                collected_blocks.append(bstr)

    if verbose:
        print(f"[*] Collected {len(collected_blocks)} blocks ({len(collected_blocks)*64} bits).")

    # Concatenate but keep as blocks so we can locate magic reliably
    bitstream = ''.join(collected_blocks)

    # Search for MAGIC in the bitstream (as bits)
    magic_bits = ''.join(f"{byte:08b}" for byte in MAGIC)
    i = bitstream.find(magic_bits)
    if i == -1:
        # Try again without undoing flips (in case flips were not done)
        if undo_flips:
            if verbose: print("[!] Magic not found with undo_flips=True, retrying with undo_flips=False...")
            return decode_robust(stego_image_path, undo_flips=False, verbose=verbose)
        raise ValueError("Magic number not found in extracted bitstream — decoding failed or wrong image/threshold.")

    if verbose:
        print(f"[*] Magic found at bit position {i} (block index {i//64}).")

    # The header layout after magic: 4 bytes size (big-endian), 8 bytes extension
    header_start = i + len(magic_bits)
    # need at least 4+8 = 12 bytes => 12*8 bits
    header_bits_needed = (4 + 8) * 8
    header_bits = bitstream[header_start:header_start + header_bits_needed]
    if len(header_bits) < header_bits_needed:
        raise ValueError("Header truncated — not enough bits after magic.")

    # Parse header
    size_bits = header_bits[:32]
    ext_bits = header_bits[32:32 + 8*8]

    file_size = int(size_bits, 2)
    ext_bytes = bytes(int(ext_bits[i:i+8], 2) for i in range(0, len(ext_bits), 8))
    # extension likely ASCII, but allow safe decode
    ext = ext_bytes.decode('ascii', errors='ignore').strip()
    if verbose:
        print(f"[*] Detected extension: '{ext}', file size: {file_size} bytes")

    # Payload starts immediately after header
    payload_start = header_start + header_bits_needed
    payload_end = payload_start + file_size * 8
    if payload_end > len(bitstream):
        raise ValueError("Not enough embedded bits for the declared file size.")

    payload_bits = bitstream[payload_start:payload_end]

    # Convert bits -> bytes
    payload = bytes(int(payload_bits[i:i+8], 2) for i in range(0, len(payload_bits), 8))

    # Save output
    out_name = f"recovered_secret{('.' + ext) if ext else ''}"
    with open(out_name, "wb") as f:
        f.write(payload)

    if verbose:
        print(f"[+] Recovered {len(payload)} bytes to '{out_name}'")

    return out_name
