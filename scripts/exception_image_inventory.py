"""Actual FD image GUID/hash/section inventory for exception PC attribution."""
import hashlib,uuid,struct,json
from uefi_firmware.uefi import FirmwareVolume,FirmwareFile
from map_oem_trace_rva import sections
def inventory(build,root):
 b=json.loads((build/'build-result.json').read_text());blob=(root/b['fd']).read_bytes()
 if hashlib.sha256(blob).hexdigest()!=b['fd_sha256']:raise ValueError('FD changed')
 volume=FirmwareVolume(blob)
 if not volume.process():raise ValueError('FD parse failed')
 queue=[volume];rows=[];seen=set()
 while queue:
  obj=queue.pop(0);queue.extend(getattr(obj,'objects',[]))
  if not isinstance(obj,FirmwareFile):continue
  pes=[s.data for s in obj.objects if s.type==0x10]
  if not pes:continue
  guid=str(uuid.UUID(bytes_le=obj.guid))
  if len(pes)!=1 or guid in seen:raise ValueError('ambiguous image inventory')
  seen.add(guid);pe=pes[0];offset=struct.unpack_from('<I',pe,60)[0]
  size=struct.unpack_from('<I',pe,offset+24+56)[0]
  rows.append(dict(guid=guid,name=next((s.data.decode('utf-16-le').rstrip('\0') for s in obj.objects if s.type==0x15),guid),pe_sha256=hashlib.sha256(pe).hexdigest(),image_size=size,sections=[dict(name=s[0],rva=s[1],bytes=s[2],file_offset=s[3],executable=bool(s[4]&0x20000000)) for s in sections(pe)]))
 return rows
