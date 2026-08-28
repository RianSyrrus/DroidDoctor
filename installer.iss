; DroidDoctor Inno Setup Script
; Author: RianSyrrus
; Architecture: Windows 64-bit (x64)

#define MyAppName "DroidDoctor"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "RianSyrrus"
#define MyAppExeName "DroidDoctor.exe"
#define MyAppIcon "assets\app_icon.ico"

[Setup]
AppId={{D1A9F8B2-5A3E-4C2B-9876-DROIDDOCTOR01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=release_v1.1.1
OutputBaseFilename=DroidDoctor-Setup-v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "release_v1.1.1\DroidDoctor-v1.1.1-Portable\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "release_v1.1.1\DroidDoctor-v1.1.1-Portable\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\app_icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
