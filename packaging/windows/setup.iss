﻿; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
; >>> http://www.jrsoftware.org/ishelp/ <<<

#define MyAppName "Watermark me!"
#define MyAppPublisher "Schoentgen Inc"
#define MyAppURL "https://github.com/BoboTiG/watermark-me"
#define MyAppUpdatesURL "https://github.com/BoboTiG/watermark-me/releases"
#define MyAppExeName "watermark.exe"

; The version must be define via an argument on calling ISCC.exe:
;    iscc /DMyAppVersion="0.1.0" setup.iss
; Same for the real product version, used for the output file:
;    iscc /DMyAppVersion="0.1.0" /DMyAppRealVersion="0.1b1" setup.iss
;#define MyAppVersion "0.1.0"
;#define MyAppRealVersion "0.1b1"


[Setup]
; NOTE: The value of AppId uniquely identifies this particular application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{382D6D46-7805-4E3F-BAAE-FC946DDB0A4A}
AppName={#MyAppName}
AppVersion={#MyAppRealVersion}
VersionInfoVersion={#MyAppVersion}
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppUpdatesURL}
AppCopyright="© 2019-2020 {#MyAppPublisher}"

; Outputs
OutputDir=../../dist
OutputBaseFilename=watermark-{#MyAppRealVersion}

; Startup menu entry: "Publisher/Application Name"
DefaultGroupName={#MyAppPublisher}
DisableProgramGroupPage=yes

; Do not require admin rights, no UAC
PrivilegesRequired=lowest

; Set the output directory to user's AppData\Local by default.
DisableDirPage=yes
DefaultDirName={localappdata}\{#MyAppName}

; Icons
UninstallDisplayIcon={app}\{#MyAppExeName}
; 256x256px, generated from a PNG with https://convertico.com/
SetupIconFile=pictures\app_icon.ico

; Pictures
; https://www.jrsoftware.org/ishelp/topic_setup_wizardimagefile.htm
WizardImageFile=pictures\wizard.bmp
; 55x58px
WizardSmallImageFile=pictures\wizard-small.bmp

; Use a modern look
WizardStyle=modern

; Other
Compression=lzma
SolidCompression=yes

; Controls which files Setup will check for being in use before upgrading
CloseApplicationsFilter=*.*


[Files]
Source: "..\..\dist\watermark\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


[UninstallDelete]
; Force the installation directory to be removed when uninstalling
Type: filesandordirs; Name: "{app}"


[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"


[Tasks]
; Create the desktop icon
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"


[Run]
; Launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall
