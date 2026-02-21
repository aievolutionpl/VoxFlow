; ═══════════════════════════════════════════════════════════════
; VoxFlow — Inno Setup Installer Script
; Requires Inno Setup 6.3+ (https://jrsoftware.org/isinfo.php)
; by AI Evolution Polska | Open Source
; ═══════════════════════════════════════════════════════════════

#define MyAppName      "VoxFlow"
#define MyAppVersion   "1.1.0"
#define MyAppPublisher "AI Evolution Polska"
#define MyAppExeName   "VoxFlow.exe"
#define MyAppURL       "https://github.com/aievolutionpl/VoxFlow"

[Setup]
; Unique GUID - do not change after first release
AppId={{B8E4F2A1-3C7D-4E9F-A5B6-1D2E3F4A5B6C}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppCopyright=Copyright © 2025 AI Evolution Polska

; Installation directory
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Output
OutputDir=installer_output
OutputBaseFilename=VoxFlow_Setup_v{#MyAppVersion}
SetupIconFile=assets\voxflow.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; Visual style
WizardStyle=modern
WizardResizable=no
WizardSizePercent=100

; Windows version requirement
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Show "This will take a moment" during extraction
ShowLanguageDialog=auto

; Restart behavior
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "polish";  MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; ─── Welcome page text ────────────────────────────────────────────
[Messages]
polish.WelcomeLabel1=Witaj w kreatorze instalacji programu [name]
polish.WelcomeLabel2=Program [name] to bezpłatne narzędzie do dyktowania głosem na komputer.%n%nDziała w 100%% offline — bez chmury, bez subskrypcji.%n%nZalecane jest zamknięcie wszystkich innych aplikacji przed kontynuowaniem.
english.WelcomeLabel1=Welcome to the [name] Setup Wizard
english.WelcomeLabel2=[name] is a free, open-source voice dictation tool for your PC.%n%nWorks 100%% offline — no cloud, no subscription required.%n%nIt is recommended that you close all other applications before continuing.

[CustomMessages]
polish.CreateDesktopShortcut=Utwórz skrót na pulpicie
polish.RunAtStartup=Uruchamiaj VoxFlow razem z Windows (zalecane)
polish.PostInstallInfo=VoxFlow został pomyślnie zainstalowany!%n%nPrzy pierwszym uruchomieniu aplikacja pobierze model AI (~500 MB). Wymagane jednorazowe połączenie z internetem.
english.CreateDesktopShortcut=Create a desktop shortcut
english.RunAtStartup=Launch VoxFlow with Windows (recommended)
english.PostInstallInfo=VoxFlow has been successfully installed!%n%nOn first launch, the app will download the AI model (~500 MB). A one-time internet connection is required.

[Tasks]
Name: "desktopicon";   Description: "{cm:CreateDesktopShortcut}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
Name: "startupentry";  Description: "{cm:RunAtStartup}";          GroupDescription: "Autostart:";             Flags: unchecked

[Files]
; Main application files (built by PyInstaller)
Source: "dist\VoxFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu
Name: "{group}\{#MyAppName}";            Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Odinstaluj {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

; Startup (optional)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: startupentry

[Registry]
; Register in "Add/Remove Programs" with additional info
Root: HKCU; Subkey: "Software\AI Evolution Polska\VoxFlow"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\AI Evolution Polska\VoxFlow"; ValueType: string; ValueName: "Version";     ValueData: "{#MyAppVersion}"

[Run]
; Offer to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "Uruchom VoxFlow teraz"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove config folder on uninstall (optional — comment out to keep user settings)
; Type: filesandordirs; Name: "{userappdata}\VoxFlow"

[Code]
// ─── Check Windows version ─────────────────────────────────────
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsWin64 then
  begin
    MsgBox('VoxFlow wymaga 64-bitowej wersji systemu Windows.' + #13#10 +
           'VoxFlow requires 64-bit Windows.', mbError, MB_OK);
    Result := False;
  end;
end;

// ─── Show info after install ────────────────────────────────────
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox(CustomMessage('PostInstallInfo'), mbInformation, MB_OK);
  end;
end;
