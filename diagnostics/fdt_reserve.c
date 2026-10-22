/* R-002: preserve all FDT node/property values, reclaim NOPs/name suffixes.
 * No allocation, MMIO, physical log access or writes on validation failure.
 * Linux boot protocol supplies a readable DTB; caller provides its capacity.
 */
#include <stdint.h>
#include <stddef.h>

static uint32_t be32(const unsigned char *p) {
    return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
}
static void put32(unsigned char *p, uint32_t n) {
    p[0]=n>>24; p[1]=n>>16; p[2]=n>>8; p[3]=n;
}
static void move(unsigned char *d, const unsigned char *s, size_t n) {
    if (d>s) { while(n) { --n; d[n]=s[n]; } }
    else { for(size_t i=0;i<n;i++) d[i]=s[i]; }
}
/* Return token extent, or zero. All arithmetic bounded by the structure end. */
static uint32_t extent(const unsigned char *b, uint32_t p, uint32_t end,
                       uint32_t so, uint32_t sn) {
    if(p>end || end-p<4) return 0;
    uint32_t t=be32(b+p), n=4;
    if(t==1) {
        uint32_t q=p+4;
        while(q<end && b[q]) q++;
        if(q==end) return 0;
        n=((q-p+1)+3)&~3u;
    } else if(t==3) {
        if(end-p<12) return 0;
        uint32_t len=be32(b+p+4), off=be32(b+p+8);
        if(len>end-p-12 || off>=sn) return 0;
        uint32_t q=off;
        while(q<sn && b[so+q]) q++;
        if(q==sn) return 0;
        n=12+((len+3)&~3u);
    } else if(t!=2 && t!=4 && t!=9) return 0;
    return n<=end-p ? n : 0;
}

struct suffix { uint32_t old, len, target; };
/* Select at most 16 complete names already available as an earlier suffix.
 * Targets stay before the first removed name, so no target is itself moved.
 * Planning is read-only. Stop as soon as one reserve tuple fits. */
static uint32_t plan_suffixes(const unsigned char *s, uint32_t sn,
                             uint32_t needed, struct suffix *plan,
                             uint32_t *saved) {
    uint32_t p=0, count=0, limit=sn; *saved=0;
    while(p<sn && count<16 && *saved<needed) {
        uint32_t end=p;
        while(end<sn && s[end]) end++;
        if(end==sn) return 0;
        uint32_t len=end-p+1, prefix=p<limit?p:limit, target=prefix;
        if(len<=prefix) for(uint32_t q=0;q<=prefix-len;q++) {
            uint32_t i=0;
            while(i<len && s[q+i]==s[p+i]) i++;
            if(i==len) {target=q;break;}
        }
        if(target<prefix) {
            if(!count) limit=p;
            plan[count++]=(struct suffix){p,len,target}; *saved+=len;
        }
        p=end+1;
    }
    return *saved>=needed?count:0;
}

/* Validated structure only: names may already contain adjusted offsets. */
static uint32_t known_extent(const unsigned char *b, uint32_t p) {
    uint32_t t=be32(b+p);
    if(t==1) {uint32_t q=p+4;while(b[q])q++;return (q-p+4)&~3u;}
    if(t==3) return 12+((be32(b+p+4)+3)&~3u);
    return 4;
}

int enuma_reserve_log(unsigned char *b, size_t capacity) {
    if(!b || capacity<56 || be32(b)!=0xd00dfeed) return 0;
    uint32_t total=be32(b+4), st=be32(b+8), so=be32(b+12);
    uint32_t sn=be32(b+32), ss=be32(b+36);
    if(total>capacity || total>0x200000 || total<56 || st!=56 ||
       be32(b+16)!=40 || be32(b+20)!=17 || be32(b+24)>17 ||
       ss>total-st || so!=st+ss || sn>total-so || (ss&3)) return 0;
    /* Only an empty original reserve map is accepted. Never merge owners. */
    for(uint32_t i=40;i<56;i++) if(b[i]) return 0;
    uint32_t p=st, end=st+ss, free_bytes=0, depth=0, seen_root=0, ended=0;
    while(p<end) {
        uint32_t n=extent(b,p,end,so,sn), t=be32(b+p);
        if(!n) return 0;
        if(t==1) {
            if(!depth && (seen_root || b[p+4])) return 0;
            seen_root=1; depth++;
        } else if(t==2) { if(!depth) return 0; depth--; }
        else if(t==3 && !depth) return 0;
        else if(t==4) free_bytes+=4;
        else if(t==9) { if(depth || !seen_root || p+n!=end) return 0; ended=1; }
        p+=n;
    }
    if(!ended) return 0;
    struct suffix plan[16]; uint32_t saved=0, count=0;
    if(free_bytes<16) {
        /* Bound pre-entry work; unsupported larger name tables stay untouched. */
        if(sn>0x20000) return 0;
        count=plan_suffixes(b+so,sn,16-free_bytes,plan,&saved);
        if(!count) return 0;
    }
    /* Validation complete: compact structure in place, retaining every token
     * except NOP. Then move structure+strings forward for one reserve tuple. */
    uint32_t dst=st; p=st;
    while(p<end) {
        uint32_t n=extent(b,p,end,so,sn);
        if(be32(b+p)!=4) { move(b+dst,b+p,n); dst+=n; }
        p+=n;
    }
    move(b+dst,b+so,sn);
    if(count) {
        uint32_t old=0, packed=0;
        for(uint32_t i=0;i<count;i++) {
            uint32_t chunk=plan[i].old-old;
            move(b+dst+packed,b+dst+old,chunk);packed+=chunk;
            old=plan[i].old+plan[i].len;
        }
        move(b+dst+packed,b+dst+old,sn-old);
        for(p=st;p<dst;) {
            if(be32(b+p)==3) {
                uint32_t off=be32(b+p+8), adjusted=off;
                for(uint32_t i=0;i<count;i++) {
                    if(off>=plan[i].old && off<plan[i].old+plan[i].len) {
                        adjusted=plan[i].target+off-plan[i].old;break;
                    }
                    if(off>=plan[i].old+plan[i].len) adjusted-=plan[i].len;
                }
                put32(b+p+8,adjusted);
            }
            p+=known_extent(b,p);
        }
    }
    move(b+st+16,b+st,dst-st+sn-saved);
    /* big-endian u64 address 0x9fff7000, size 0x8000, then terminator */
    put32(b+40,0); put32(b+44,0x9fff7000);
    put32(b+48,0); put32(b+52,0x8000);
    for(uint32_t i=56;i<72;i++) b[i]=0;
    put32(b+8,st+16); put32(b+12,dst+16); put32(b+32,sn-saved);
    put32(b+36,ss-free_bytes);
    return 1;
}

#ifdef ENUMA_ARM64_ENTRY
void enuma_fdt_entry(unsigned char *b) {
    if(!b || ((uintptr_t)b&7)) return;
    /* Fail closed to the untouched stock Android path. Runtime host guard
     * must observe the actual reservation before any readback/marker test. */
    if(enuma_reserve_log(b,0x200000)) {
        uintptr_t ctr, end=(uintptr_t)b+be32(b+4);
        __asm__ volatile("mrs %0, ctr_el0":"=r"(ctr));
        uintptr_t line=4ul<<((ctr>>16)&15);
        for(uintptr_t p=(uintptr_t)b&~(line-1);p<end;p+=line)
            __asm__ volatile("dc cvac, %0"::"r"(p):"memory");
        __asm__ volatile("dsb sy":::"memory");
    }
}
#endif
