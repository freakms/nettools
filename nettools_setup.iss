; NetTools Suite - Inno Setup Script
; Creates Windows installer with component selection

#define MyAppName "NetTools Suite"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company"
#define MyAppURL "https://yourwebsite.com"
#define MyAppExeName "NetTools.exe"

[Setup]
; Basic app information
AppId={{A1B2C3D4-E5F6-4A5B-8C7D-9E8F7A6B5C4D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=NetTools_Setup_{#MyAppVersion}
; SetupIconFile=network_icon.ico  ; Uncomment if you have an icon file
Compression=lzma2/max
SolidCompression=yes

; Windows version requirements
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern
DisableWelcomePage=no
LicenseFile=LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Types]
Name: "full"; Description: "Full Installation (All Tools)"
Name: "standard"; Description: "Standard Installation (Most Common Tools)"
Name: "minimal"; Description: "Minimal Installation (Core Tools Only)"
Name: "custom"; Description: "Custom Installation"; Flags: iscustom

[Components]
; Core - Always installed
Name: "core"; Description: "NetTools Core Application"; Types: full standard minimal custom; Flags: fixed

; Network Scanning Tools
Name: "scanning"; Description: "Network Scanning Tools"; Types: full standard custom
Name: "scanning\ipv4"; Description: "IPv4 Scanner"; Types: full standard custom; Flags: fixed
Name: "scanning\portscan"; Description: "Port Scanner"; Types: full standard custom
Name: "scanning\traceroute"; Description: "Traceroute & Pathping"; Types: full standard custom
Name: "scanning\livemon"; Description: "Live Ping Monitor"; Types: full standard custom
Name: "scanning\bandwidth"; Description: "Bandwidth Testing (requires iperf3)"; Types: full custom

; Network Utilities
Name: "utilities"; Description: "Network Utility Tools"; Types: full standard custom
Name: "utilities\dns"; Description: "DNS Lookup"; Types: full standard custom
Name: "utilities\subnet"; Description: "Subnet Calculator"; Types: full standard custom
Name: "utilities\mac"; Description: "MAC Address Formatter"; Types: full standard custom

; Management Tools
Name: "management"; Description: "Management & Analysis Tools"; Types: full custom
Name: "management\compare"; Description: "Scan Comparison"; Types: full custom
Name: "management\profiles"; Description: "Network Profiles"; Types: full custom

; Advanced Tools
Name: "advanced"; Description: "Advanced Professional Tools"; Types: full custom
Name: "advanced\panos"; Description: "PAN-OS CLI Generator"; Types: full custom
Name: "advanced\phpipam"; Description: "phpIPAM Integration"; Types: full custom

; Optional Dependencies
Name: "dependencies"; Description: "Optional Dependencies"; Types: full custom
Name: "dependencies\iperf3"; Description: "Install iperf3 (for Bandwidth Testing)"; Types: full

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Core application files (always installed)
Source: "dist\NetTools\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Documentation (optional - only if files exist)
Source: "*.md"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; iperf3 (optional - bundled, only if exists)
Source: "external\iperf3.exe"; DestDir: "{app}\tools"; Flags: ignoreversion skipifsourcedoesntexist; Components: dependencies\iperf3

[Icons]
; Start menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Documentation"; Filename: "{app}\docs"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to run after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; Add iperf3 to PATH if installed
Filename: "powershell.exe"; Parameters: "-Command ""[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';{app}\tools', 'Machine')"""; Flags: runhidden; Components: dependencies\iperf3

[Code]
var
  ComponentsPage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  // Create custom component selection page
  ComponentsPage := CreateInputOptionPage(wpSelectComponents,
    'Select Tools to Install', 'Choose which network tools you want to install',
    'Select the components you want to install, then click Next.',
    False, False);
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create configuration file based on installed components
    SaveStringToFile(ExpandConstant('{app}\installed_components.txt'), 
                    'Components installed: ' + WizardSelectedComponents(False), False);
  end;
end;

[Registry]
; Add to Windows PATH for iperf3
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\tools"; Components: dependencies\iperf3; Check: NeedsAddPath('{app}\tools')

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

[UninstallDelete]
Type: files; Name: "{app}\installed_components.txt"
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{localappdata}\NetTools"
