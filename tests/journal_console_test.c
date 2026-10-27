// SPDX-License-Identifier: BSD-2-Clause-Patent
// Actual attributed formatter and ConOut sink, real pinned EDK UEFI types.
#include "EnumaJournalConsole.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static ENUMA_BOOT_LOG Live, Snapshot;
static char Transcript[32768];
static unsigned Used, Calls, Snapshots;
static unsigned FailureAt;
static EFI_STATUS OutputStatus;
static BOOLEAN SnapshotOk=TRUE;
static EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL Out;
static EFI_GUID Guid={0x11223344,0x5566,0x7788,{0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0}};

static EFI_STATUS EFIAPI Output(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This, CHAR16 *Text) {
  assert(This==&Out); Calls++;
  for (unsigned I=0; Text[I]; I++) {
    assert(Text[I]<128 && Used+1<sizeof Transcript);
    Transcript[Used++]=(char)Text[I];
  }
  Transcript[Used]=0;
  return FailureAt && Calls!=FailureAt?EFI_SUCCESS:OutputStatus;
}
static BOOLEAN EFIAPI Copy(ENUMA_BOOT_LOG *Target) {
  Snapshots++;
  if (!SnapshotOk) { return FALSE; }
  *Target=Live; return TRUE;
}
static void ResetOutput(void) { Used=Calls=FailureAt=0; Transcript[0]=0; OutputStatus=EFI_SUCCESS; }
static void Replay(void) {
  UINT32 Cursor=0; ENUMA_JOURNAL_CONSOLE Sink={&Out,EFI_SUCCESS};
  while (Cursor<=Snapshot.Count) {
    assert(EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink));
  }
  assert(Calls==Snapshot.Count+1);
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink));
}
static void Save(const char *Path) {
  FILE *F=fopen(Path,"wb"); assert(F);
  assert(fwrite(Transcript,1,Used,F)==Used); assert(!fclose(F));
}
int main(int Argc, char **Argv) {
  assert(Argc==3); Out.OutputString=Output;
  ENUMA_BOOT_JOURNAL_PROTOCOL Journal={1,sizeof(Journal),Copy};
  ENUMA_JOURNAL_CONSOLE Sink={&Out,EFI_SUCCESS}; UINT32 Cursor;
  assert(EnumaJournalConsoleSnapshot(NULL,&Out,&Snapshot)==EFI_INVALID_PARAMETER);
  assert(EnumaJournalConsoleSnapshot(&Journal,NULL,&Snapshot)==EFI_NOT_READY && !Snapshots);
  Journal.Version=2;
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_INCOMPATIBLE_VERSION && !Snapshots);
  Journal.Version=1; Journal.Bytes--;
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_INCOMPATIBLE_VERSION);
  Journal.Bytes=sizeof Journal; Journal.Snapshot=NULL;
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_INCOMPATIBLE_VERSION);
  Journal.Snapshot=Copy; SnapshotOk=FALSE;
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_DEVICE_ERROR && !Calls);
  SnapshotOk=TRUE;
  assert(EnumaBootLogAppend(&Live,15,7,&Guid,0));
  assert(EnumaBootLogAppend(&Live,20,7,&Guid,0));
  assert(EnumaBootLogAppend(&Live,21,7,&Guid,0x8000000000000001ULL));
  assert(EnumaBootLogAppend(&Live,22,7,&Guid,0x8000000000000001ULL));
  assert(EnumaBootLogAppend(&Live,13,7,&Guid,0x8000000000000001ULL));
  assert(EnumaBootLogAppend(&Live,15,7,&Guid,0)); // current provider has not returned
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_SUCCESS);
  ResetOutput(); Replay();
  assert(strstr(Transcript,"phase=before-start o=00000007 s=not-returned"));
  assert(strstr(Transcript,"phase=entry-return o=00000007 s=8000000000000001"));
  assert(strstr(Transcript,"guid=11223344-5566-7788-99aa-bbccddeeff00\r\n"));
  Save(Argv[1]);
  // Failed OutputString can already have printed the line; no cursor progress
  // and no hidden retry. Caller must stop rather than assume exactly-once.
  ResetOutput(); OutputStatus=EFI_DEVICE_ERROR; Cursor=0;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink));
  assert(Cursor==0 && Calls==1 && Used>0 && Sink.LastStatus==EFI_DEVICE_ERROR);
  ResetOutput(); OutputStatus=EFI_WARN_UNKNOWN_GLYPH;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink));
  assert(Cursor==0 && Calls==1 && Sink.LastStatus==EFI_WARN_UNKNOWN_GLYPH);
  ResetOutput(); Sink.Output=NULL;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink));
  assert(!Calls && Cursor==0 && Sink.LastStatus==EFI_NOT_READY); Sink.Output=&Out;
  assert(!EnumaJournalConsoleSink(&Sink,"bad\r\n",5) && !Calls);
  assert(!EnumaJournalConsoleSink(&Sink,"bad\001\n",5) && !Calls);
  assert(!EnumaJournalConsoleSink(&Sink,"no LF",5) && !Calls);
  assert(!EnumaJournalConsoleSink(&Sink,NULL,0) && !Calls);
  assert(!EnumaJournalConsoleSink(&Sink,"x\n",192) && !Calls);
  Snapshot.Events[0].Sequence=99;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink) && !Calls);
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_SUCCESS);
  Snapshot.Dropped=1;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink) && !Calls);
  Snapshot=Live;Snapshot.Count--;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink) && !Calls);
  Snapshot=Live;Snapshot.Events[0].HasGuid=2;
  assert(!EnumaBootLogReplayAttributedNext(&Snapshot,&Cursor,EnumaJournalConsoleSink,&Sink) && !Calls);
  assert(EnumaConsoleWriteLine(NULL,L"test")==EFI_NOT_READY);
  assert(EnumaConsoleWriteLine(&Out,NULL)==EFI_INVALID_PARAMETER);
  CHAR16 Long[129]; for(unsigned I=0;I<128;I++) { Long[I]=L'a'; } Long[128]=0;
  assert(EnumaConsoleWriteLine(&Out,Long)==EFI_BAD_BUFFER_SIZE && !Calls);
  Long[127]=0;
  assert(EnumaConsoleWriteLine(&Out,Long)==EFI_SUCCESS && Calls==1 && Used==129);
  ResetOutput(); assert(EnumaConsoleWriteLine(&Out,L"test")==EFI_SUCCESS);
  assert(!strcmp(Transcript,"test\r\n"));
  ResetOutput();OutputStatus=EFI_DEVICE_ERROR;
  assert(EnumaConsoleWriteLine(&Out,L"test")==EFI_DEVICE_ERROR && Calls==1);
  // Wrap, all supported phases plus arbitrary checkpoints, full-width values,
  // missing GUID, all-ones GUID and no false returned status for checkpoints.
  memset(&Live,0,sizeof Live); memset(&Guid,255,sizeof Guid);
  for (unsigned I=0;I<200;I++) {
    unsigned Points[]={13,14,15,20,21,22,99};
    assert(EnumaBootLogAppend(&Live,Points[I%7],0xffffffffu,I%2?&Guid:NULL,MAX_UINT64));
  }
  assert(EnumaJournalConsoleSnapshot(&Journal,&Out,&Snapshot)==EFI_SUCCESS);
  ResetOutput(); Replay(); Save(Argv[2]);
  assert(strstr(Transcript,"dropped=0000000000000048"));
  assert(strstr(Transcript,"phase=checkpoint o=ffffffff s=not-a-return"));
  UINT32 Accepted=999;
  ResetOutput();assert(EnumaJournalConsoleDrain(&Snapshot,&Out,&Accepted)==EFI_SUCCESS);
  assert(Accepted==129 && Calls==129);
  for(unsigned Kind=0;Kind<2;Kind++) for(unsigned At=1;At<=129;At++) {
    ResetOutput();FailureAt=At;OutputStatus=Kind?EFI_WARN_UNKNOWN_GLYPH:EFI_DEVICE_ERROR;
    assert(EnumaJournalConsoleDrain(&Snapshot,&Out,&Accepted)==OutputStatus);
    assert(Calls==At && Accepted==At-1); // Partial failing line never counted/retried.
  }
  ResetOutput();Snapshot.Dropped++;
  assert(EnumaJournalConsoleDrain(&Snapshot,&Out,&Accepted)==EFI_COMPROMISED_DATA && !Calls && !Accepted);
  Snapshot.Dropped--;
  assert(EnumaJournalConsoleDrain(&Snapshot,NULL,&Accepted)==EFI_NOT_READY && !Calls);
  assert(EnumaJournalConsoleDrain(&Snapshot,&Out,NULL)==EFI_INVALID_PARAMETER && !Calls);
  for(unsigned Kind=0;Kind<2;Kind++) {
    ResetOutput();ENUMA_JOURNAL_CONSOLE Session={&Out,EFI_SUCCESS};
    OutputStatus=Kind?EFI_WARN_UNKNOWN_GLYPH:EFI_DEVICE_ERROR;
    EFI_STATUS First=OutputStatus;
    assert(EnumaConsoleSessionWriteLine(&Session,L"partial")==First && Calls==1);
    OutputStatus=EFI_SUCCESS;
    assert(EnumaConsoleSessionWriteLine(&Session,L"do not resume")==First && Calls==1);
  }
  puts("PASS: bounded129-line drain,258 failing output positions, no implicit retry; sticky first warning/error");
  puts("PASS: attributed GUID/phase/status, in-progress return distinction, wrapped snapshot, ConOut ABI/null/error/warning/partial-output/CRLF/bounds and no implicit retry");
  return 0;
}
