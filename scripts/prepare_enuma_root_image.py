"""Decode pinned iPadOS OS/SystemOS into a local SHNGROOT file, never a device.

Uses the fixed upstream UDIF reader used by the Linux/fajita route. Partition
capacity and APFS mount/owner policy remain independent, unverified inputs.
"""
import argparse,hashlib,json,os,struct,subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MIB=1<<20
INPUTS=[('OS','044-76040-038.dmg','3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d',
         'e5634d04a8ac35f024845f583394e0a35deb26a04cb0c00286a8674e25a9a4f2',6077580800),
        ('SystemOS','044-76034-038.dmg','b4908cde41d23e6bc05e6af51a2c9eeb00cf0f863a6a18b1600c96a3fd70414f',
         'b4908cde41d23e6bc05e6af51a2c9eeb00cf0f863a6a18b1600c96a3fd70414f',3303014400)]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(8*MIB):h.update(b)
    return h.hexdigest()
def header(entries,total):
    h=bytearray(4096);h[:8]=b'SHNGROOT';struct.pack_into('<IIQ',h,8,1,len(entries),total)
    for i,e in enumerate(entries):
        struct.pack_into('<32sQQII32s40s',h,24+128*i,e['name'].encode(),e['offset'],e['bytes'],512,1,bytes.fromhex(e['sha256']),bytes(40))
    h[4064:]=hashlib.sha256(h[:4064]).digest();return h
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--components',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    ref=a.reference.resolve();pin='16e592abee8a550dec8154ed1f38b5ebc4f16213';sources={}
    for n in ['scripts/unixnu/udif.py','scripts/unixnu/util.py','scripts/unixnu/__init__.py','scripts/unixnu/userdata.py']:
        data=(ref/n).read_bytes();fixed=subprocess.check_output(['git','-C',str(ref),'show',pin+':'+n])
        if data!=fixed:raise ValueError('UDIF reference changed '+n)
        sources[n]=hashlib.sha256(data).hexdigest()
    decoder=Path('/mnt/d/Code/PortingiOSLegacy/common/tools/apfs-fuse-linux/bin/lzfse')
    if sha(decoder)!='f89442c9e68063b115df9fcc6defa96c9f5affedc44fa6751dc4d67d3c18c4d4':raise ValueError('LZFSE decoder changed')
    os.environ['UNIXNU_TOOLCHAIN']=str(decoder.parent.parent)
    sys.path.insert(0,str(ref/'scripts'));from unixnu.udif import Image
    entries=[];cursor=MIB
    for name,member,digest,raw_digest,size in INPUTS:
        path=a.components/member;print('Verifying cached '+name,flush=True)
        if sha(path)!=digest:raise ValueError('compressed donor digest mismatch '+name)
        if Image(path).size!=size:raise ValueError('expanded geometry mismatch '+name)
        entries.append(dict(name=name,member=member,offset=cursor,bytes=size,sha256=raw_digest,source_sha256=digest))
        cursor+=(size+MIB-1)//MIB*MIB
    if shutil.disk_usage(out).free<cursor+MIB:raise ValueError('insufficient host disk space')
    image=out/'root-components.img'
    with image.open('xb') as target:
        target.truncate(cursor)
        for e in entries:
            print('Decoding '+e['name'],flush=True);target.seek(e['offset']);h=hashlib.sha256();done=0
            for data in Image(a.components/e['member']).blocks():
                if len(data)>e['bytes']-done:raise ValueError('decoder exceeded window')
                target.write(data);h.update(data);done+=len(data)
            if done!=e['bytes'] or h.hexdigest()!=e['sha256']:raise ValueError('expanded donor digest mismatch '+e['name'])
        block=header(entries,cursor);target.seek(0);target.write(block)
    # Independent file readback of each published range, not just write-time hashes.
    with image.open('rb') as f:
        if f.read(4096)!=block:raise ValueError('manifest readback differs')
        for e in entries:
            f.seek(e['offset']);remaining=e['bytes'];h=hashlib.sha256()
            while remaining:
                data=f.read(min(remaining,8*MIB))
                if not data:raise ValueError('truncated root file')
                h.update(data);remaining-=len(data)
            if h.hexdigest()!=e['sha256']:raise ValueError('root window readback differs')
    result=dict(passed=True,image_bytes=cursor,image_sha256=sha(image),manifest_sha256=hashlib.sha256(block).hexdigest(),
        windows=entries,udif_commit=pin,udif_sources=sources,decoder_sha256=sha(decoder),
        hardware_executed=False,partition_capacity_checked=False,data_seed_included=False,apfs_mounted=False,
        root_uuid_verified=False,scope='local root component file; no GPT geometry, flash command or desktop readiness')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: decoded and reread both root windows',flush=True)
if __name__=='__main__':main()
