"""Hash/line bound source-order and sink dependency audit; no compile or device."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    files={};edges=[]
    def ordered(path,*tokens):
        p=ROOT/path;text=p.read_text();previous=-1;anchors=[]
        for token in tokens:
            expected=2 if token=='    Status = Console->OutputString (Console, Buffer);' else 1
            assert text.count(token)==expected,(path,token,text.count(token))
            pos=text.index(token);assert pos>previous,(path,token,'order changed');previous=pos
            anchors.append(dict(line=text[:pos].count('\n')+1,text=token))
        files[path]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),anchors=anchors)
        return anchors
    ordered('firmware/patches/dxe-dispatch-details.patch',
        '+        EnumaDispatchDetailCheckpoint (15, &DriverEntry->FileName, EFI_SUCCESS);',
        '         Status = CoreStartImage (DriverEntry->ImageHandle, NULL, NULL);',
        '+        EnumaDispatchDetailCheckpoint (13, &DriverEntry->FileName, Status);')
    ordered('firmware/diagnostics/EnumaInheritedVideoAudit.c',
        'if(Status==EnumaInheritedOk&&Reason==EnumaVideoReasonComplete&&mEvidence.Frame.Requirements==22)',
        'if(Policy!=3||El!=4||!gBS||!gBS->LocateProtocol||',
        'Journal->Version!=1||Journal->Bytes!=sizeof(*Journal)||!Journal->Snapshot||',
        '!Journal->Snapshot(&mReplaySnapshot)||!EnumaLogPageFromSnapshot(&mReplaySnapshot,&mEnumaLogPage)',
        'return (EFI_STATUS)PixelArmProbe(&mEvidence.Frame,Policy,El);')
    ordered('firmware/diagnostics/EnumaDispatchDetailCheckpoint.h',
        'EnumaJournalPublishAttempted=TRUE;',
        'EnumaJournalPublishStatus=CoreInstallProtocolInterface(',
        '  EnumaJournalPublish();',
        '  (VOID) EnumaBootLogAppend (&EnumaDxeBootLog, (UINT32)Point,')
    ordered('firmware/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c',
        '  Print (L"%s\\n", Text);','  DiagDraw (Text, Row);',
        '  Status = UniXNURun (ImageHandle, UniXNUHostFirmware);')
    ordered('firmware/Mu_Basecore/MdePkg/Library/UefiLib/UefiLibPrint.c',
        '    Status = Console->OutputString (Console, Buffer);',
        '  Return = InternalPrint (Format, gST->ConOut, Marker);')
    ordered('firmware/Mu_Basecore/MdeModulePkg/Universal/BdsDxe/BdsEntry.c',
        '  PlatformBootManagerBeforeConsole ();','    EfiBootManagerConnectAllDefaultConsoles ();',
        '  PlatformBootManagerAfterConsole ();')
    ordered('firmware/Silicon/Silicium/SiliciumPkg/Library/BootManagerLib/BootManager.c',
        '  EfiBootManagerUpdateConsoleVariable (ConOut, (EFI_DEVICE_PATH_PROTOCOL *)&DisplayDevicePath, NULL);')
    ordered('firmware/Platforms/Xiaomi/enumaPkg/Include/PlatformConfig.inc',
        'SerialPortLib|MdePkg/Library/BaseSerialPortLibNull/BaseSerialPortLibNull.inf')
    prefix='out/sources/UniXNU/package/UniXNUPkg/Library/UniXNULib/'
    ordered(prefix+'Main.c','  DEBUG ((PcdGet32 (PcdUniXNUDebugLevel), "%a", Line));',
        '    mSerial->Write (mSerial, &Size, Line);','    UniXNUConnectAll ();',
        '  UniXNUConfigLoad (ImageHandle, &Config);','  UniXNUInjectDrivers (ImageHandle, &Config, &Stats);',
        '  UniXNUUiInit (&Config, &Ui);','    Index  = UniXNUMenuRun (&Ui, &Config, Countdown);')
    ordered(prefix+'Ui.c','  Ui->Mode = UniXNUUiHeadless;',
        '      Status = gBS->HandleProtocol (gST->ConsoleOutHandle, &gEfiGraphicsOutputProtocolGuid, (VOID **)&Ui->Gop);',
        '      Status = gBS->LocateProtocol (&gEfiGraphicsOutputProtocolGuid, NULL, (VOID **)&Ui->Gop);',
        '      Ui->Mode   = UniXNUUiGraphics;',
        '    if (!EFI_ERROR (gST->ConOut->QueryMode (gST->ConOut, gST->ConOut->Mode->Mode, &Ui->TextColumns, &Ui->TextRows))) {',
        '      Ui->Mode = UniXNUUiText;')
    ordered('firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/PixelLogPage.h',
        '    if(E->Point==13) { Event=E;break; }',
        "  Page->Text[0][4]='O';EnumaBootLogHex(&Page->Text[0][5],Event->Ordinal,8);",
        "  Page->Text[1][0]='S';EnumaBootLogHex(&Page->Text[1][1],Event->Status>>32,8);",
        '  EnumaBootLogHex(&Page->Text[2][1],Event->Status&0xffffffffu,8);',
        '  Page->Sequence=Event->Sequence;Page->Ready=TRUE;return 1;')
    ordered('out/firmware-build/uefi/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/DarwinProbe.inc',
        'DiagDraw (CONST CHAR16 *Text, UINTN Row)',
        '  if (EFI_ERROR (gBS->LocateProtocol (&gEfiGraphicsOutputProtocolGuid, NULL, (VOID **)&Gop)) ||',
        '        Fb[(Y + Gy) * (Video[2] / 4) + X + Gx] = 0xFF000000;',
        '              Fb[(Y + Gy * Scale + Dy) * (Video[2] / 4) + X + Gx * Scale + Dx] = 0xFFFFFFFF;')
    links=json.loads((ROOT/'reports/enuma-console-path-audit.json').read_text())
    for name,entries in links['links'].items():
        assert entries,name
        for e in entries:
            p=ROOT/e['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']
            assert e['null_serial'] and not e['framebuffer_serial'] and e['serial_debug']
    q=json.loads((ROOT/'reports/enuma-native-route-qualification.json').read_text())
    frozen=json.loads((ROOT/q['archive']/'qualification.json').read_text());assert frozen==q
    assert q['hardware_review']=='R-022' and q['hold_us']==8000000 and not q['review_required']
    assert hashlib.sha256((ROOT/q['image']).read_bytes()).hexdigest()==q['image_sha256']
    result=dict(scope='source-order/sink dependencies and actual existing static-link lists; no new firmware build or runtime proof',
        sources=files,frozen_r022_image_sha256=q['image_sha256'],firmware_commit=q['firmware_commit'],
        source_order_findings=dict(current_invocation_return_not_yet_recorded_during_snapshot=True,
          newest_point13_can_belong_to_prior_driver=True,page_omits_guid_and_sequence=True,
          publish_attempt_once_without_retry=True,snapshot_single_writer_quiescent_contract=True,
          bds_connection_precedes_after_console=True,probe_print_and_diagdraw_are_two_independent_writes=True,
          unixnu_log_targets_debug_and_optional_serialio_not_conout=True,
          unixnu_drivers_precede_ui=True,ui_has_graphics_then_text_then_headless_paths=True),
        actual_link_bindings=links['links'],
        limitations=['Source order is not executed-path evidence','Patch series is reverted by official backend after build; current unpatched staging is not actual compiled Core source','R022 PE review is separately bound to frozen packaged binaries','Snapshot ABI has no concurrency lock or exception/AP guarantee','SerialIo protocol availability is not established by Null SerialPortLib binding'],
        hardware_executed=False,device_action=False,screen_log_verified=False,global_debug=False,gop_admitted=False,menu_executed=False)
    (ROOT/'reports/enuma-console-readiness.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: source order and6 module link lists; frozen R022 unchanged; no hardware proof')
if __name__=='__main__':main()
