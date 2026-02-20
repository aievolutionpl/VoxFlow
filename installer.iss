; VoxFlow Installer Script for Inno Setup
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)

#define MyAppName "VoxFlow"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AI Evolution Polska"
#define MyAppExeName "VoxFlow.exe"
#define MyAppURL "https://github.com/aievolutionpl/VoxFlow"

[Setup]
AppId={{B8E4F2A1-3C7D-4E9F-A5B6-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=VoxFlow_Setup_v1.0.0
SetupIconFile=assets\voxflow.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe ikony:"; Flags: unchecked
Name: "startupicon"; Description: "Uruchamiaj VoxFlow razem z Windows"; GroupDescription: "Autostart:"; Flags: unchecked

[Files]
Source: "dist\VoxFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Odinstaluj {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Uruchom VoxFlow"; Flags: nowait postinstall skipifsilent
