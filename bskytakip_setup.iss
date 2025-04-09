[Setup]
AppName=Bluesky Takipçi Kontrol
AppVersion=1.0
DefaultDirName={autopf}\BlueskyTakipciKontrol
DefaultGroupName=Bluesky Takipçi Kontrol
OutputDir=dist
OutputBaseFilename=bskytakip_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=logo.ico
AllowNoIcons=yes
DisableDirPage=no

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Files]
Source: "dist\bskytakip.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Bluesky Takipçi Kontrol"; Filename: "{app}\bskytakip.exe"
Name: "{group}\Programı Kaldır"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\bskytakip.exe"; Description: "{cm:LaunchProgram,Bluesky Takipçi Kontrol}"; Flags: nowait postinstall skipifsilent
