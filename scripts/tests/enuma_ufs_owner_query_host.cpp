// Host dependency model only. The test runner inserts the actual query TU,
// r4 UFS authentication methods and actual IOKitBSDInit publication function.
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <openssl/sha.h>
// XNU names the SHA-384 state SHA384_CTX; OpenSSL uses SHA512_CTX for both.
using SHA384_CTX = SHA512_CTX;
#include <sys/types.h>
#include "verified_root.h"
#define major(d) ((uint32_t(d) >> 24) & 255)
#define minor(d) (uint32_t(d) & 0xffffff)
#define makedev(a,b) ((uint32_t(a) << 24) | uint32_t(b))
#define NODEV dev_t(-1)
#define OSDynamicCast(t,p) dynamic_cast<t *>(p)
#define OSSafeReleaseNULL(p) do { if (p) (p)->release(); (p) = nullptr; } while (0)
static size_t strlcpy(char *d, const char *s, size_t n) {
  size_t z = strlen(s); if (n) { size_t k = z < n-1 ? z : n-1; memcpy(d,s,k); d[k]=0; } return z;
}
struct OSObject { virtual ~OSObject() = default; void release() {} };
struct OSString : OSObject {
  std::string value;
  static OSString *withCString(const char *s) { auto *p = new OSString; p->value=s; return p; }
  size_t getLength() const { return value.size(); }
  const char *getCStringNoCopy() const { return value.c_str(); }
};
struct OSNumber : OSObject {
  uint64_t value;
  static OSNumber *withNumber(uint64_t v, unsigned) { auto *p=new OSNumber; p->value=v; return p; }
  uint32_t unsigned32BitValue() const { return uint32_t(value); }
  uint64_t unsigned64BitValue() const { return value; }
};
struct OSDictionary : OSObject {
  std::map<std::string,OSObject *> values;
  static OSDictionary *withCapacity(unsigned) { return new OSDictionary; }
  bool setObject(const char *s, OSObject *p) { values[s]=p; return true; }
};
struct OSData : OSObject {
  std::vector<uint8_t> data;
  static OSData *withBytes(const void *s, size_t n) { auto *p=new OSData; auto *b=(const uint8_t *)s; p->data.assign(b,b+n); return p; }
};
struct IORegistryEntry : OSObject {
  std::map<std::string,OSObject *> properties;
  OSObject *getProperty(const char *s) { auto it=properties.find(s); return it==properties.end()?nullptr:it->second; }
  bool setProperty(const char *s, OSObject *p) { properties[s]=p; return true; }
  void removeProperty(const char *s) { properties.erase(s); }
  static IORegistryEntry *fromPath(const char *, const char *);
};
struct OSIterator : OSObject {
  std::vector<OSObject *> entries; size_t at=0;
  OSObject *getNextObject() { return at<entries.size()?entries[at++]:nullptr; }
};
struct IOService : IORegistryEntry {
  IOService *parent=nullptr;
  IOService *getProvider() { return parent; }
  static OSDictionary *serviceMatching(const char *) { return OSDictionary::withCapacity(1); }
  static OSIterator *getMatchingServices(OSDictionary *);
};
static const char *kIOBSDMajorKey="major", *kIOBSDMinorKey="minor", *kIOBSDNameKey="name", *gIODTPlane="IODeviceTree";
static std::vector<IOService *> registry;
static IORegistryEntry chosen;
IORegistryEntry *IORegistryEntry::fromPath(const char *path, const char *) { assert(!strcmp(path,"/chosen")); return &chosen; }
OSIterator *IOService::getMatchingServices(OSDictionary *matching) {
  auto *result=new OSIterator;
  auto *properties=dynamic_cast<OSDictionary *>(matching->values.at("IOPropertyMatch"));
  for (auto *media:registry) {
    bool same=true;
    for (auto &item:properties->values) {
      auto *actual=media->getProperty(item.first.c_str());
      if (auto *wanted=dynamic_cast<OSNumber *>(item.second)) {
        auto *number=dynamic_cast<OSNumber *>(actual); same &= number && number->value==wanted->value;
      } else if (auto *wanted=dynamic_cast<OSString *>(item.second)) {
        auto *text=dynamic_cast<OSString *>(actual); same &= text && text->value==wanted->value;
      } else assert(false);
    }
    if (same) result->entries.push_back(media);
  }
  return result;
}
static bool IOGetBootManifestHash(char *dst, size_t *length) {
  auto *value=dynamic_cast<OSData *>(chosen.getProperty("boot-manifest-hash"));
  if (!value || *length<value->data.size()) return false;
  memcpy(dst,value->data.data(),value->data.size()); *length=value->data.size(); return true;
}
class NativeUfsBlock : public IOService {
public:
  bool online=true;
  uintptr_t verifiedStorage=0;
  vr_view verified={};
  bool authenticatesVolume(const char *, uint8_t * = nullptr) const;
};
extern "C" { volatile int native_owner_boot_manifest_status=-1; uint8_t native_owner_boot_manifest_hash[48]; }

// INSERT_ACTUAL_IMPLEMENTATIONS

static std::vector<uint8_t> load(const char *path) {
  std::ifstream file(path,std::ios::binary); assert(file.good());
  return std::vector<uint8_t>(std::istreambuf_iterator<char>(file),{});
}
static std::string hex(const uint8_t *p, size_t n) {
  static const char h[]="0123456789abcdef"; std::string s;
  for(size_t i=0;i<n;++i){s+=h[p[i]>>4];s+=h[p[i]&15];}return s;
}
static IOService *media(const char *uuid, unsigned number, NativeUfsBlock *window) {
  auto *p=new IOService; p->parent=window;
  p->setProperty("UUID",OSString::withCString(uuid));
  p->setProperty(kIOBSDMajorKey,OSNumber::withNumber(14,32));
  p->setProperty(kIOBSDMinorKey,OSNumber::withNumber(number,32));
  p->setProperty(kIOBSDNameKey,OSString::withCString(number==10?"disk10s1":"disk11s1"));return p;
}
static void bind(NativeUfsBlock &w, std::vector<uint8_t> &data) {
  memcpy(w.verified.volume_uuid,data.data()+40,16);
  memcpy(&w.verified.block_count,data.data()+32,8);
  // Put allocation padding and a fake adjacent key after the real envelope.
  // The inserted real UFS method must never include either in SHA384.
  data.resize(data.size()+8192+395,0xa5);
  w.verified.hashes=data.data()+VR_HEADER_BYTES+VR_SIGNATURE_BYTES;
  w.verifiedStorage=reinterpret_cast<uintptr_t>(data.data());
}
int main(int argc,char **argv) {
  assert(argc==5); auto os=load(argv[1]), cache=load(argv[2]);
  assert(os.size()==47481664 && cache.size()==25805344);
  NativeUfsBlock rootWindow,cacheWindow; bind(rootWindow,os);bind(cacheWindow,cache);
  auto *root=media(argv[3],10,&rootWindow), *system=media(argv[4],11,&cacheWindow);
  registry={root,system}; dev_t rd=makedev(14,10),cd=makedev(14,11),selected=NODEV;char path[64];uint8_t digest[48];
  assert(native_verified_block_root_authorized(rd)==1);
  assert(native_verified_block_volume_device(argv[3],&selected,path,sizeof path)==1 && selected==rd && !strcmp(path,"/dev/disk10s1"));
  assert(native_verified_block_manifest_sha384(rd,argv[3],digest)==1);printf("OS=%s\n",hex(digest,48).c_str());
  assert(native_verified_block_manifest_sha384(cd,argv[4],digest)==1);printf("SYSTEMOS=%s\n",hex(digest,48).c_str());
  auto reject=[&](const char *uuid){memset(digest,0xa5,48);assert(!native_verified_block_manifest_sha384(rd,uuid,digest));assert(hex(digest,48)==std::string(96,'0'));};
  auto *duplicate=media(argv[3],10,&rootWindow); registry.push_back(duplicate);reject(argv[3]);
  assert(!native_verified_block_volume_device(argv[3],&selected,path,sizeof path) && selected==NODEV && !path[0]);
  registry={root,system,media(argv[3],12,&rootWindow)};
  assert(!native_verified_block_volume_device(argv[3],&selected,path,sizeof path));
  registry={root,system};std::string wrong=argv[3];wrong[0]=wrong[0]=='0'?'1':'0';reject(wrong.c_str());
  root->setProperty("UUID",OSString::withCString(wrong.c_str()));reject(wrong.c_str());root->setProperty("UUID",OSString::withCString(argv[3]));
  IOService ordinary;root->parent=&ordinary;reject(argv[3]);
  ordinary.parent=&rootWindow;assert(native_verified_block_root_authorized(rd));
  rootWindow.online=false;reject(argv[3]);rootWindow.online=true;
  uintptr_t storage=rootWindow.verifiedStorage;rootWindow.verifiedStorage=0;reject(argv[3]);rootWindow.verifiedStorage=storage;
  std::vector<std::unique_ptr<IOService>> chain;
  IOService *next=&rootWindow;
  for(int i=0;i<62;++i){auto p=std::make_unique<IOService>();p->parent=next;next=p.get();chain.push_back(std::move(p));}
  root->parent=next;assert(native_verified_block_root_authorized(rd));
  IOService extra;extra.parent=next;root->parent=&extra;reject(argv[3]);root->parent=&rootWindow;
  root->setProperty(kIOBSDMajorKey,OSNumber::withNumber(256,32));assert(!native_verified_block_volume_device(argv[3],&selected,path,sizeof path));root->setProperty(kIOBSDMajorKey,OSNumber::withNumber(14,32));
  root->setProperty(kIOBSDNameKey,OSString::withCString(""));assert(!native_verified_block_volume_device(argv[3],&selected,path,sizeof path));root->setProperty(kIOBSDNameKey,OSString::withCString("disk10s1"));
  assert(native_owner_publish_boot_manifest(rd,argv[3],cd,argv[4])==1);
  printf("BOOTSET=%s\n",hex(native_owner_boot_manifest_hash,48).c_str());
  auto *domain=dynamic_cast<OSData *>(chosen.getProperty("owner-boot-manifest-domain"));assert(domain && domain->data.size()==sizeof("VerifiedRoot.OwnerBootSet.v1") && !memcmp(domain->data.data(),"VerifiedRoot.OwnerBootSet.v1",domain->data.size()));
  assert(!native_owner_publish_boot_manifest(rd,argv[3],cd,argv[4]) && native_owner_boot_manifest_status==3);
  printf("CASES=unique,duplicate-device,duplicate-uuid,wrong-expected-uuid,wrong-signed-uuid,non-ufs,ancestor-dispatch,offline-window,missing-verification,depth64,depth65,devt-bound,path-bound,owner-domain,preexisting-chosen\n");
}
