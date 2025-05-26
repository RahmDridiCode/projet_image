from collections import Counter
import heapq

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data):
    frequency = Counter(data)
    heap = [Node(ch, freq) for ch, freq in frequency.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(None, n1.freq + n2.freq)
        merged.left = n1
        merged.right = n2
        heapq.heappush(heap, merged)
    return heap[0]

def build_codes(node, prefix="", code_map={}):
    if node is None:
        return
    if node.char is not None:
        code_map[node.char] = prefix
    build_codes(node.left, prefix + "0", code_map)
    build_codes(node.right, prefix + "1", code_map)
    return code_map

def huffman_compress(data):
    tree = build_huffman_tree(data)
    code_map = build_codes(tree, code_map={})
    encoded = ''.join(code_map[byte] for byte in data)
    return encoded, code_map

def shannon_fano_encode(symbols):
    if len(symbols) == 1:
        return {symbols[0][0]: "0"}
    
    total = sum(freq for _, freq in symbols)
    acc = 0
    split_idx = 0
    for i, (_, freq) in enumerate(symbols):
        acc += freq
        if acc >= total / 2:
            split_idx = i + 1
            break
    left = symbols[:split_idx]
    right = symbols[split_idx:]

    codes = {}
    codes_left = shannon_fano_encode(left)
    codes_right = shannon_fano_encode(right)

    for symbol in codes_left:
        codes[symbol] = "0" + codes_left[symbol]
    for symbol in codes_right:
        codes[symbol] = "1" + codes_right[symbol]

    return codes

def shannon_fano_compress(data):
    frequency = Counter(data).most_common()
    code_map = shannon_fano_encode(frequency)
    encoded = ''.join(code_map[byte] for byte in data)
    return encoded, code_map

def decode_binary_to_bytes(encoded_data, code_map):
    reverse_map = {v: k for k, v in code_map.items()}
    decoded_bytes = bytearray()

    buffer = ""
    for bit in encoded_data:
        buffer += bit
        if buffer in reverse_map:
            decoded_bytes.append(int(reverse_map[buffer]))
            buffer = ""
    return bytes(decoded_bytes)
