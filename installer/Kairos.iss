#define MyAppName "Kairos"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Thomas Hallberg"
#define MyAppExeName "Kairos.exe"

[Setup]
AppId={{B7A4B32D-5B6D-4C67-9E69-47E3C16B7D42}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=output
OutputBaseFilename=KairosSetup

Compression=lzma2
SolidCompression=yes

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=admin
WizardStyle=modern

UninstallDisplayName={#MyAppName}

SetupIconFile=..\assets\kairos.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist_gui_v4\Kairos\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Kairos"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall Kairos"; Filename: "{uninstallexe}"

[Code]
function OllamaInstalled(): Boolean;
begin
  Result :=
    FileExists(ExpandConstant('{localappdata}\Programs\Ollama\ollama.exe')) or
    FileExists(ExpandConstant('{userappdata}\..\Local\Programs\Ollama\ollama.exe')) or
    FileExists(ExpandConstant('{pf}\Ollama\ollama.exe'));
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ErrorCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if not OllamaInstalled() then
    begin
      if MsgBox(
        'Kairos använder Ollama för att köra AI lokalt på din dator.' + #13#10 + #13#10 +
        'Ollama verkar inte vara installerat.' + #13#10 +
        'Vill du öppna Ollamas officiella nedladdningssida?',
        mbInformation,
        MB_YESNO
      ) = IDYES then
      begin
        ShellExec(
          'open',
          'https://ollama.com/download/windows',
          '',
          '',
          SW_SHOWNORMAL,
          ewNoWait,
          ErrorCode
        );
      end;
    end;
  end;
end;