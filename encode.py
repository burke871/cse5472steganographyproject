import os
from PIL import Image
import numpy as np

BLOCK = 8
THRESHOLD = 0.40

def prepare_secret_blocks(secret_file):
    # Read file
    with open(secret_file, "rb") as f:
        data = f.read()

    # File size and extension
    size_bytes = len(data).to_bytes(4, byteorder='big')
    ext = os.path.splitext(secret_file)[1].encode('ascii')
    ext_bytes = ext.ljust(8, b'\x00')  # pad to 8 bytes
    magic = b"BPCS"

    # Combine header + file
    full_bytes = magic + size_bytes + ext_bytes + data

    # Convert to 64-bit blocks
    bitstream = ''.join(format(byte, '08b') for byte in full_bytes)
    blocks = [bitstream[i:i+64].ljust(64, '0') for i in range(0, len(bitstream), 64)]
    print(f"[+] Secret file size: {len(data)} bytes")
    print(f"[+] Total secret 64-bit blocks (with header): {len(blocks)}")
    return blocks

def segment_bitplane(bitplane, block_size=8, threshold=0.4):
    h, w = bitplane.shape

    informative_blocks = []
    noise_blocks = []

    for i in range(0, h, block_size):
        for j in range(0, w, block_size):

            block = bitplane[i:i+block_size, j:j+block_size]

            # Ensure block is full size (pad if image not divisible)
            if block.shape != (block_size, block_size):
                continue

            alpha = block_complexity(block)

            if alpha >= threshold:
                noise_blocks.append(((i, j), block))
            else:
                informative_blocks.append(((i, j), block))

    return informative_blocks, noise_blocks

def block_complexity(block):
        transitions = 0

        # Horizontal transitions
        for r in range(BLOCK):
            for c in range(BLOCK - 1):
                if block[r][c] != block[r][c+1]:
                    transitions += 1

        # Vertical transitions
        for c in range(BLOCK):
            for r in range(BLOCK - 1):
                if block[r][c] != block[r+1][c]:
                    transitions += 1

        max_transitions = (BLOCK * (BLOCK - 1)) * 2
        return transitions / max_transitions

# Convert uint8 image array to array of 8-bit binary strings
def int2bitarray(img_array):
    h, w = img_array.shape
    arr = np.empty((h, w), dtype=object)
    for i in range(h):
        for j in range(w):
            arr[i, j] = format(img_array[i, j], '08b')
    return arr


def encode(vessel_image, secret_message):
    # --- Load vessel image in RGB ---
    img = Image.open(vessel_image).convert('RGB')
    r, g, b = img.split()
    r_array, g_array, b_array = np.array(r), np.array(g), np.array(b)
    h, w = r_array.shape

    # --- Convert each channel to bitstrings ---
    r_bits = int2bitarray(r_array)
    g_bits = int2bitarray(g_array)
    b_bits = int2bitarray(b_array)

    # --- Load secret blocks ---
    secret_blocks = prepare_secret_blocks(secret_message)
    secret_index = 0

    # --- Prepare bitplanes for each channel ---
    channels = {'R': r_bits, 'G': g_bits, 'B': b_bits}
    stego_bitplanes = {'R': [], 'G': [], 'B': []}

    for ch_name, ch_bits in channels.items():
        for k in range(8):
            plane = np.zeros((h, w), dtype=np.uint8)

            # Fill plane from channel bits
            for i in range(h):
                for j in range(w):
                    plane[i, j] = int(ch_bits[i, j][k])

            # Only segment/embed if there is still secret data
            if secret_index < len(secret_blocks):
                informative_blocks, noise_blocks = segment_bitplane(plane)
                print(f"{ch_name}-channel bitplane {7-k}: {len(noise_blocks)} noise-like blocks, {len(informative_blocks)} informative blocks")

                # Embed secret blocks into noise-like blocks
                for idx, ((bi, bj), _) in enumerate(noise_blocks):
                    if secret_index >= len(secret_blocks):
                        break
                    sblock = np.array([int(b) for b in secret_blocks[secret_index]], dtype=np.uint8).reshape(BLOCK, BLOCK)
                    plane[bi:bi+BLOCK, bj:bj+BLOCK] = sblock
                    secret_index += 1

            stego_bitplanes[ch_name].append(plane.copy())

        # No break here — always create 8 bitplanes per channel
        # This avoids empty bitplanes for G/B if secret finished in R

    print(f"[+] Total secret blocks embedded: {secret_index}/{len(secret_blocks)}")

    # --- Recombine bitplanes into stego channels ---
    def recombine_planes(bitplanes):
        array = np.zeros((h, w), dtype=np.uint8)
        for i in range(h):
            for j in range(w):
                bits = ''.join(str(bitplanes[k][i, j]) for k in range(8))
                array[i, j] = int(bits, 2)
        return array

    r_stego = recombine_planes(stego_bitplanes['R'])
    g_stego = recombine_planes(stego_bitplanes['G'])
    b_stego = recombine_planes(stego_bitplanes['B'])

    # --- Flip vertically to match PyQt preview (optional) ---
    r_stego = np.flipud(r_stego)
    g_stego = np.flipud(g_stego)
    b_stego = np.flipud(b_stego)

    r_stego = np.fliplr(r_stego)
    g_stego = np.fliplr(g_stego)
    b_stego = np.fliplr(b_stego)

    # --- Merge channels and save ---
    stego_img = Image.merge("RGB", (
        Image.fromarray(r_stego),
        Image.fromarray(g_stego),
        Image.fromarray(b_stego)
    ))
    stego_img.save("stego_image.png")
    print(f"[+] Secret embedded, saved as 'stego_image.png'")