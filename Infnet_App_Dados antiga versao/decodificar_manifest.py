# ==============================================================================
# SCRIPT: decodificar_manifest.py
# DATA/HORA: 29/10/2026 15:43
# FINALIDADE: Decodifica o AndroidManifest.xml binario (AXML) do APK em XML legivel
# ==============================================================================

import struct
import os

axml_path = r"C:\Users\matth\Desktop\Infnet_App_Dados\conteudo_extraido\AndroidManifest.xml"
out_path = r"C:\Users\matth\Desktop\Infnet_App_Dados\conteudo_extraido\AndroidManifest_LEGIVEL.xml"

with open(axml_path, "rb") as f:
    data = f.read()

# Header: magic (4 bytes), size (4 bytes)
magic, size = struct.unpack_from("<II", data, 0)
if magic != 0x00080003:
    print(f"Formato inesperado: {hex(magic)}")
    exit(1)

# String pool chunk
sp_header, sp_size, str_count, style_count, flags, str_offset, style_offset = struct.unpack_from("<IIIIIII", data, 8)
is_utf8 = bool(flags & (1 << 8))

str_offsets = [struct.unpack_from("<I", data, 8 + 28 + i * 4)[0] for i in range(str_count)]
strings_data_start = 8 + str_offset

strings = []
for off in str_offsets:
    p = strings_data_start + off
    if is_utf8:
        # u8 length
        u16len = data[p]
        p += 1
        if u16len & 0x80:
            u16len = ((u16len & 0x7F) << 8) | data[p]
            p += 1
        u8len = data[p]
        p += 1
        if u8len & 0x80:
            u8len = ((u8len & 0x7F) << 8) | data[p]
            p += 1
        s = data[p:p + u8len].decode("utf-8", errors="replace")
    else:
        u16len = struct.unpack_from("<H", data, p)[0]
        p += 2
        if u16len & 0x8000:
            u16len = ((u16len & 0x7FFF) << 16) | struct.unpack_from("<H", data, p)[0]
            p += 2
        s = data[p:p + u16len * 2].decode("utf-16le", errors="replace")
    strings.append(s)

# Process XML tags
p = 8 + sp_size
xml_lines = ['<?xml version="1.0" encoding="utf-8"?>']
indent = 0

while p < len(data):
    if p + 8 > len(data):
        break
    chunk_type, chunk_size = struct.unpack_from("<II", data, p)
    if chunk_size == 0:
        break
    
    if chunk_type == 0x00100100: # START_NAMESPACE
        line, comment, prefix_idx, uri_idx = struct.unpack_from("<IIII", data, p + 8)
    elif chunk_type == 0x00100102: # START_ELEMENT
        line, comment, ns_idx, name_idx, attr_start, attr_size, attr_count, id_idx, class_idx, style_idx = struct.unpack_from("<IIIIHHHHHH", data, p + 8)
        tag_name = strings[name_idx] if name_idx < len(strings) else "tag"
        attrs = []
        attr_ptr = p + 8 + 20
        for _ in range(attr_count):
            a_ns, a_name, a_val_str, a_type, a_data = struct.unpack_from("<IIIII", data, attr_ptr)
            attr_ptr += 20
            aname = strings[a_name] if a_name < len(strings) else f"attr_{a_name}"
            if a_ns < len(strings) and strings[a_ns]:
                aname = "android:" + aname
            if a_val_str != 0xFFFFFFFF and a_val_str < len(strings):
                aval = strings[a_val_str]
            else:
                aval = str(a_data)
                if (a_type >> 24) == 0x12: # boolean
                    aval = "true" if a_data != 0 else "false"
                elif (a_type >> 24) == 0x01: # reference
                    aval = f"@ref/0x{a_data:08x}"
            attrs.append(f'{aname}="{aval}"')
        
        attr_str = " " + " ".join(attrs) if attrs else ""
        xml_lines.append("  " * indent + f"<{tag_name}{attr_str}>")
        indent += 1
    elif chunk_type == 0x00100103: # END_ELEMENT
        line, comment, ns_idx, name_idx = struct.unpack_from("<IIII", data, p + 8)
        tag_name = strings[name_idx] if name_idx < len(strings) else "tag"
        indent = max(0, indent - 1)
        xml_lines.append("  " * indent + f"</{tag_name}>")
    
    p += chunk_size

formatted_xml = "\n".join(xml_lines)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(formatted_xml)

print(f"[OK] XML legivel gerado com sucesso em: {out_path}")
