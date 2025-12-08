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
Name: "scanning\bandwidth"; Description: "Bandwidth Testing (requires manual iperf3 installation)"; Types: full custom

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

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Core application files (always installed)
Source: "dist\NetTools\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Documentation (optional - only if files exist)
Source: "*.md"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

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

[Code]
var
  BandwidthTestingSelected: Boolean;
  InfoPage: TOutputMsgMemoWizardPage;

procedure InitializeWizard;
begin
  BandwidthTestingSelected := False;
  
  // Create information page for external dependencies
  InfoPage := CreateOutputMsgMemoPage(wpInfoAfter,
    'Important Information - External Dependencies',
    'Additional software may be required for some features',
    'Please review the information below:',
    '');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // Only show info page if bandwidth testing was selected
  if PageID = InfoPage.ID then
    Result := not BandwidthTestingSelected
  else
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InfoText: string;
begin
  if CurStep = ssPostInstall then
  begin
    // Create configuration file based on installed components
    SaveStringToFile(ExpandConstant('{app}\installed_components.txt'), 
                    'Components installed: ' + WizardSelectedComponents(False), False);
    
    // Check if bandwidth testing component was selected
    if WizardIsComponentSelected('scanning\bandwidth') then
    begin
      BandwidthTestingSelected := True;
      
      // Prepare information text about iperf3
      InfoText := 'BANDWIDTH TESTING TOOL - iperf3 Required' + #13#10 + #13#10;
      InfoText := InfoText + 'You have selected the Bandwidth Testing tool, which requires iperf3 to be installed separately.' + #13#10 + #13#10;
      InfoText := InfoText + 'To use this feature, please:' + #13#10;
      InfoText := InfoText + '1. Download iperf3 for Windows from:' + #13#10;
      InfoText := InfoText + '   https://iperf.fr/iperf-download.php' + #13#10 + #13#10;
      InfoText := InfoText + '2. Extract iperf3.exe to a folder (e.g., C:\Tools\iperf3\)' + #13#10 + #13#10;
      InfoText := InfoText + '3. Add the folder to your Windows PATH:' + #13#10;
      InfoText := InfoText + '   - Right-click "This PC" > Properties > Advanced system settings' + #13#10;
      InfoText := InfoText + '   - Click "Environment Variables"' + #13#10;
      InfoText := InfoText + '   - Under "System variables", find and edit "Path"' + #13#10;
      InfoText := InfoText + '   - Add the iperf3 folder path' + #13#10 + #13#10;
      InfoText := InfoText + '4. Restart NetTools application after installation' + #13#10 + #13#10;
      InfoText := InfoText + 'The Bandwidth Testing tool will not work until iperf3 is properly installed.';
      
      InfoPage.RichEditViewer.Text := InfoText;
    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\installed_components.txt"
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{localappdata}\NetTools"
