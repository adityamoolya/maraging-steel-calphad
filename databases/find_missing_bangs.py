with open('databases/mc_fe_v2062.tdb', 'r', encoding='latin-1') as f:
    lines = f.readlines()

current_block = []
block_start_line = -1

for idx, line in enumerate(lines):
    line_num = idx + 1
    cleaned = line.strip()
    if not cleaned or cleaned.startswith('$'):
        continue
    
    # If we find a new major keyword, check if the previous block was terminated
    first_word = cleaned.split()[0].upper() if cleaned.split() else ""
    
    if first_word in ['ELEMENT', 'PHASE', 'CONSTITUENT', 'PARAMETER', 'FUNCTION', 'TYPE_DEFINITION', 'DEFINE_SYSTEM_MODEST']:
        if current_block and not current_block[-1].endswith('!'):
            print(f"Block starting at line {block_start_line} was not terminated before line {line_num}:")
            print("  Previous block text:", " ".join(current_block))
            print("  New line:", cleaned)
        current_block = [cleaned]
        block_start_line = line_num
    else:
        if current_block:
            current_block.append(cleaned)

if current_block and not current_block[-1].endswith('!'):
    print(f"Block starting at line {block_start_line} was not terminated at EOF.")
