import os
import PySimpleGUI as gui
import platform
import wimport os
import PySimpleGUI as gui
import platform
import webbrowser
import sys
import ctypes
import shutil
from pkg_resources import parse_version
from button import RoundedButton
import darkdetect
from os.path import exists
import requests
from configparser import ConfigParser

# Block usage on non Windows OS
if(platform.system() != "Windows"):
    print("This operating system is not supported.")
    sys.exit(0)

ctypes.windll.shcore.SetProcessDpiAwareness(True) # Make program DPI aware

version = "1.3.7"
adbRunning = False
msixfolder = os.getenv('LOCALAPPDATA') + "\\Packages\\46954GamenologyMedia.WSASideloader-APKInstaller_cjpp7y4c11e3w\\LocalState"

config = ConfigParser()
configpath = 'config.ini'

if darkdetect.isDark():
    gui.theme("LightGrey")
    gui.theme_background_color("#232020")
    gui.theme_text_element_background_color("#232020")
    gui.theme_text_color("White")
    gui.theme_button_color(('#232020', '#ADD8E6'))
    gui.theme_input_background_color('#ADD8E6')
    gui.theme_input_text_color('#000000')
else:
    gui.theme("LightGrey")

def startgit(filearg = ""):
    global installsource
    installsource = "GitHub (via git clone)"
    global explorerfile
    explorerfile = filearg
    # Check if OS is Windows 11
    if int(platform.win32_ver()[1].split('.')[2]) < 22000:
        layout = [[gui.Text('You need Windows 11 to use WSA Sideloader (as well as the subsystem itself). Please upgrade your operating system and install WSA before running this program.\nFor more information and support, visit the WSA Sideloader GitHub page.',font=("Calibri",11))],
                [RoundedButton("Exit",0.3,font="Calibri 11"),RoundedButton("GitHub",0.3,font="Calibri 11")]]
        window = gui.Window('Unsupported OS', layout,icon="icon.ico",debugger_enabled=False)

        event, values = window.Read()
        if event == "GitHub":
            window.Close()
            webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader/",2)
            sys.exit(0)
        elif event is None or "Exit":
            sys.exit(0)
        window.Close()
        
    main()
    
def startstore(filearg = ""): # For Microsoft Store installs
    global installsource
    installsource = "Microsoft Store"
    global explorerfile
    explorerfile = filearg
    if os.path.isdir(msixfolder+'\\platform-tools') == False: # Check if platform tools present
        shutil.copytree("platform-tools",msixfolder + "\\platform-tools")
        copyfiles = ['icon.ico','aapt.exe']
        for f in copyfiles:
            shutil.copy(f,msixfolder)
        os.chdir(msixfolder)
        main()
    else:
        os.chdir(msixfolder)
        main()

def start(filearg = ""): # For GitHub installs
    global installsource
    installsource = "GitHub"
    global explorerfile
    explorerfile = filearg
    global configpath
    configpath = os.getenv('LOCALAPPDATA') + "\\WSA Sideloader\\config.ini"
    try:
        response = requests.get("https://api.github.com/repos/infinitepower18/WSA-Sideloader/releases/latest")
        latestver = response.json()["name"]
        latestver = latestver[16:]
        if parse_version(latestver) > parse_version(version):
            layout = [[gui.Text('A newer version of WSA Sideloader is available.\nWould you like to update now?',font=("Calibri",11))],
                [RoundedButton("Yes",0.3,font="Calibri 11"),RoundedButton("No",0.3,font="Calibri 11")]]
            window = gui.Window('Update available', layout,icon="icon.ico",debugger_enabled=False)
            event, values = window.Read()
            if event is None:
                sys.exit(0)
            elif event == "Yes":
                window.Close()
                webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader/releases/latest",2)
                sys.exit(0)
            elif event == "No":
                window.Close()
                main()
        else:
            main()
    except requests.exceptions.RequestException as error: # Skip update check in case of network error
        main()

def startWSA(window): # Start subsystem if not running
    webbrowser.open("wsa://system",2)
    window.Hide()
    startingLayout = [[gui.Text("WSA Sideloader is attempting to start the subsystem.\nIf it's properly installed, you should see a separate window saying it's starting.\nOnce it closes, click OK to go back and try again.",font=("Calibri",11))],[RoundedButton('OK',0.3,font="Calibri 11")]]
    startingWindow = gui.Window("Message",startingLayout,icon="icon.ico",debugger_enabled=False)
    while True:
        event,values = startingWindow.Read()
        if event is None:
            sys.exit(0)
        elif event == "OK":
            startingWindow.Close()
            window.UnHide()
            break

def main():
    global adbRunning
    adbAddress = "127.0.0.1:58526"
    try:
        config.read(configpath)
        adbAddress = config.get('Application','adbAddress')
    except:
        if not os.path.exists(os.getenv('LOCALAPPDATA') + "\\WSA Sideloader"):
            os.makedirs(os.getenv('LOCALAPPDATA') + "\\WSA Sideloader")
        config['Application'] = {'adbAddress':'127.0.0.1:58526'}
        with open(configpath, 'w') as configfile:
            config.write(configfile)
    # Main window
    layout = [[gui.Text('APKを選択してください:',font="Yu Gothic UI 11")],
            [gui.Input(explorerfile,font="Yu Gothic UI 11"),gui.FileBrowse(file_types=(("APK ファイル","*.apk"),),font="Yu Gothic UI 11")],
            [RoundedButton("APKの権限を表示",0.3,font="Yu Gothic UI 11")],
            [gui.Text('Error message',key='_ERROR1_',visible=False,font="Yu Gothic UI 11")],
            [gui.Text('ADB アドレス:',font="Yu Gothic UI 11")],
            [gui.Input(adbAddress,font="Yu Gothic UI 11")],
            [RoundedButton('インストール',0.3,font="Yu Gothic UI 11"),RoundedButton('インストール済みのアプリ',0.3,font="Yu Gothic UI 11"),RoundedButton('Help',0.3,font="Calibri 11"),RoundedButton('バージョン情報',0.3,font="Yu Gothic UI 11")],
            [gui.Text("Error message",key='_ERROR2_',visible=False,font="Yu Gothic UI 11")]]

    window = gui.Window('WSA Sideloader', layout,icon="icon.ico",debugger_enabled=False)

    while True:
        event, values = window.Read()
        if event is None:
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
        if event == "View APK permissions":
            source_filename = values[0]
            if os.path.exists(source_filename) == False:
                window['_ERROR1_'].Update("APK file not found")
                window["_ERROR1_"].Update(visible=True)
            elif source_filename.endswith(".apk") == False:
                window['_ERROR1_'].Update("Only APK files are supported")
                window["_ERROR1_"].Update(visible=True)
            else:
                source_filename = values[0]
                window.Hide()
                gui.popup_scrolled(os.popen('cmd /c "aapt d permissions "'+source_filename+'""').read(),size=(100,10),icon="icon.ico",title="APK permissions")
                window.UnHide()
        if event == "Installed apps": # Launch apps list of com.android.settings
            config.set('Application','adbAddress',values[1])
            with open(configpath, 'w') as configfile:
                config.write(configfile)
            autostart = os.popen('cmd /c "tasklist"')
            startoutput = str(autostart.readlines())
            if "WsaClient.exe" not in startoutput:
                startWSA(window)
            else:
                try:
                    window['_ERROR2_'].Update("Loading installed apps...")
                    window["_ERROR2_"].Update(visible=True)
                    address = values[1]
                    address = address.replace(" ", "")
                    adbRunning = True
                    command = os.popen('cmd /c "cd platform-tools & adb connect '+address+' & adb -s '+address+' shell am start -n "com.android.settings/.applications.ManageApplications""')
                    output = command.readlines()
                    check = str(output[len(output)-1])
                    if check.startswith("Starting: Intent { cmp=com.android.settings/.applications.ManageApplications }"):
                        window["_ERROR2_"].Update(visible=False)
                    else:
                        window['_ERROR2_'].Update("Please check that WSA is running and the correct ADB address\nhas been entered.\nRestart your computer if you continue to see this error.")
                        window["_ERROR2_"].Update(visible=True)
                except IndexError:
                    window['_ERROR2_'].Update("ADB address cannot be empty")
                    window["_ERROR2_"].Update(visible=True)
        if event == "Install":
            config.set('Application','adbAddress',values[1])
            with open(configpath, 'w') as configfile:
                config.write(configfile)
            source_filename = values[0]
            address = values[1]
            address = address.replace(" ", "")
            if source_filename == "":
                window['_ERROR2_'].Update("Please select an APK file.")
                window["_ERROR2_"].Update(visible=True)
            elif exists(source_filename) == False:
                window['_ERROR2_'].Update("File not found")
                window["_ERROR2_"].Update(visible=True)
            elif source_filename.endswith(".apk") == False:
                window['_ERROR2_'].Update("Only APK files are supported")
                window["_ERROR2_"].Update(visible=True)
            else:
                if address == "":
                    window['_ERROR2_'].Update("ADB address cannot be empty")
                    window["_ERROR2_"].Update(visible=True)
                else:
                    autostart = os.popen('cmd /c "tasklist"')
                    startoutput = str(autostart.readlines())
                    if "WsaClient.exe" in startoutput:
                        break
                    else:
                        startWSA(window)
        if event == "Help":
            window.Hide()
            helpLayout = [[gui.Text("このプログラムはWindows Subsystem for AndroidにAPKファイルをインストールするために使用する物です:\n1. Windows Subsystem for Androidが導入済みである事\n2. 開発者向けオプションの有効化 (スタートメニュー内のWindows Subsystem for Androidの設定から有効化)\nWSA Sideloaderはファイルエクスプローラーやその他のサポート可能なプログラムと統合されているので、ファイルをダブルクリックのみでインストールが可能にする事ができます。詳細とサポートはGitHubのページにてご確認ください。",font=("Yu Gothic UI",11))],[RoundedButton("戻る",0.3,font="Yu Gothic UI 11"),RoundedButton("GitHub",0.3,font="Yu Gothic UI 11"),RoundedButton("対応しているアプリ",0.3,font="Yu Gothic UI 11")]]
            helpWindow = gui.Window('Help',helpLayout,icon="icon.ico",debugger_enabled=False)
            while True:
                event,values = helpWindow.Read()
                if event is None:
                    if adbRunning == True:
                        os.popen('cmd /c "cd platform-tools & adb kill-server"')
                    sys.exit(0)
                elif event == "戻る":
                    helpWindow.Close()
                    window.UnHide()
                    break
                elif event == "GitHub":
                    webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader",2)
                elif event == "対応しているアプリ":
                    webbrowser.open("https://github.com/riverar/wsa-app-compatibility",2)
        if event == "バージョン情報":
            window.Hide()
            abtLayout = [[gui.Text('WSA SideloaderはWindows Subsystem for AndroidにAPKファイルを簡単にインストールするツールです。',font="Yu Gothic UI 11")],[gui.Text("バージョン: "+version,font="Yu Gothic UI 11")],[gui.Text("ダウンロード元: "+installsource,font="Yu Gothic UI 11")],[RoundedButton("戻る",0.3,font="Yu Gothic UI 11"),RoundedButton("GitHub",0.3,font="Yu Gothic UI 11")]]
            abtWindow = gui.Window('バージョン情報',abtLayout,icon="icon.ico",debugger_enabled=False)
            while True:
                event,values = abtWindow.Read()
                if event is None:
                    if adbRunning == True:
                        os.popen('cmd /c "cd platform-tools & adb kill-server"')
                    sys.exit(0)
                elif event == "Back":
                    abtWindow.Close()
                    window.UnHide()
                    break
                elif event == "GitHub":
                    webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader",2)

    window.Close()

    layout = [[gui.Text('アプリをインストール中です...',font=("Yu Gothic UI",11))]]
    window = gui.Window('お待ちください...', layout,no_titlebar=True,keep_on_top=True,debugger_enabled=False)
    event, values = window.Read(timeout=0)
    adbRunning = True
    command = os.popen('cmd /c "cd platform-tools & adb connect '+address+' & adb -s '+address+' install "'+source_filename+'""') # Command to install APK
    output = command.readlines()
    check = str(output[len(output)-1])
    window.Close()
    
    # Check if apk installed successfully
    if check.startswith("Success"):
        layout = [[gui.Text('アプリのインストールが成功しました。',font=("Yu Gothic UI",11))],
                [RoundedButton("アプリを開く",0.3,font="Yu Gothic UI 11"),RoundedButton("他のAPKをインストール",0.3,font="Yu Gothic UI 11")]]
        window = gui.Window('Information', layout,icon="icon.ico",debugger_enabled=False)

        event, values = window.Read()
        if event == "Open app":
            getpackage = os.popen('cmd /c "aapt d permissions "'+source_filename+'""')
            pkgoutput = getpackage.readlines()
            pkgname = str(pkgoutput[0])
            webbrowser.open("wsa://"+pkgname[9:],2)
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
        elif event == "Install another APK":
            window.Close()
            main()
        else:
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
    else:
        layout = [[gui.Text('WSA Sideloaderはアプリのインストールに失敗しました:\n有効なAPKである事\nWSAが実行中である事\n開発者向けオプションの有効か確認をしてください。\nこのエラーが表示され続けている場合は、PCを再起動後にもう再度試してみてください。',font=("Yu Gothic UI",11))],
                [RoundedButton("OK",0.3,font="Yu Gothic UI 11"),RoundedButton("バグを報告する",0.3,font="Yu Gothic UI 11")]]
        window = gui.Window('Error', layout,icon="icon.ico",debugger_enabled=False)

        event, values = window.Read()
        if event == "OK":
            window.Close()
            main()
        elif event == "Report a bug": # Open WSA Sideloader issues page
            window.Close()
            webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader/issues",2)
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
        else:
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    if len(sys.argv) >1:
        startgit(sys.argv[1])
    else:
        startgit()
ebbrowser
import sys
import ctypes
import shutil
from pkg_resources import parse_version
from button import RoundedButton
import darkdetect
from os.path import exists
import requests
from configparser import ConfigParser

# Block usage on non Windows OS
if(platform.system() != "Windows"):
    print("This operating system is not supported.")
    sys.exit(0)

ctypes.windll.shcore.SetProcessDpiAwareness(True) # Make program DPI aware

version = "1.3.7"
adbRunning = False
msixfolder = os.getenv('LOCALAPPDATA') + "\\Packages\\46954GamenologyMedia.WSASideloader-APKInstaller_cjpp7y4c11e3w\\LocalState"

config = ConfigParser()
configpath = 'config.ini'

if darkdetect.isDark():
    gui.theme("LightGrey")
    gui.theme_background_color("#232020")
    gui.theme_text_element_background_color("#232020")
    gui.theme_text_color("White")
    gui.theme_button_color(('#232020', '#ADD8E6'))
    gui.theme_input_background_color('#ADD8E6')
    gui.theme_input_text_color('#000000')
else:
    gui.theme("LightGrey")

def startgit(filearg = ""):
    global installsource
    installsource = "GitHub (via git clone)"
    global explorerfile
    explorerfile = filearg
    # Check if OS is Windows 11
    if int(platform.win32_ver()[1].split('.')[2]) < 22000:
        layout = [[gui.Text('You need Windows 11 to use WSA Sideloader (as well as the subsystem itself). Please upgrade your operating system and install WSA before running this program.\nFor more information and support, visit the WSA Sideloader GitHub page.',font=("Calibri",11))],
                [RoundedButton("Exit",0.3,font="Calibri 11"),RoundedButton("GitHub",0.3,font="Calibri 11")]]
        window = gui.Window('Unsupported OS', layout,icon="icon.ico",debugger_enabled=False)

        event, values = window.Read()
        if event == "GitHub":
            window.Close()
            webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader/",2)
            sys.exit(0)
        elif event is None or "Exit":
            sys.exit(0)
        window.Close()
        
    main()
    
def startstore(filearg = ""): # For Microsoft Store installs
    global installsource
    installsource = "Microsoft Store"
    global explorerfile
    explorerfile = filearg
    if os.path.isdir(msixfolder+'\\platform-tools') == False: # Check if platform tools present
        shutil.copytree("platform-tools",msixfolder + "\\platform-tools")
        copyfiles = ['icon.ico','aapt.exe']
        for f in copyfiles:
            shutil.copy(f,msixfolder)
        os.chdir(msixfolder)
        main()
    else:
        os.chdir(msixfolder)
        main()

def start(filearg = ""): # For GitHub installs
    global installsource
    installsource = "GitHub"
    global explorerfile
    explorerfile = filearg
    global configpath
    configpath = os.getenv('LOCALAPPDATA') + "\\WSA Sideloader\\config.ini"
    try:
        response = requests.get("https://api.github.com/repos/infinitepower18/WSA-Sideloader/releases/latest")
        latestver = response.json()["name"]
        latestver = latestver[16:]
        if parse_version(latestver) > parse_version(version):
            layout = [[gui.Text('A newer version of WSA Sideloader is available.\nWould you like to update now?',font=("Calibri",11))],
                [RoundedButton("Yes",0.3,font="Calibri 11"),RoundedButton("No",0.3,font="Calibri 11")]]
            window = gui.Window('Update available', layout,icon="icon.ico",debugger_enabled=False)
            event, values = window.Read()
            if event is None:
                sys.exit(0)
            elif event == "Yes":
                window.Close()
                webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader/releases/latest",2)
                sys.exit(0)
            elif event == "No":
                window.Close()
                main()
        else:
            main()
    except requests.exceptions.RequestException as error: # Skip update check in case of network error
        main()

def startWSA(window): # Start subsystem if not running
    webbrowser.open("wsa://system",2)
    window.Hide()
    startingLayout = [[gui.Text("WSA Sideloader is attempting to start the subsystem.\nIf it's properly installed, you should see a separate window saying it's starting.\nOnce it closes, click OK to go back and try again.",font=("Calibri",11))],[RoundedButton('OK',0.3,font="Calibri 11")]]
    startingWindow = gui.Window("Message",startingLayout,icon="icon.ico",debugger_enabled=False)
    while True:
        event,values = startingWindow.Read()
        if event is None:
            sys.exit(0)
        elif event == "OK":
            startingWindow.Close()
            window.UnHide()
            break

def main():
    global adbRunning
    adbAddress = "127.0.0.1:58526"
    try:
        config.read(configpath)
        adbAddress = config.get('Application','adbAddress')
    except:
        if not os.path.exists(os.getenv('LOCALAPPDATA') + "\\WSA Sideloader"):
            os.makedirs(os.getenv('LOCALAPPDATA') + "\\WSA Sideloader")
        config['Application'] = {'adbAddress':'127.0.0.1:58526'}
        with open(configpath, 'w') as configfile:
            config.write(configfile)
    # Main window
    layout = [[gui.Text('Choose APK file to install:',font="Calibri 11")],
            [gui.Input(explorerfile,font="Calibri 11"),gui.FileBrowse(file_types=(("APK files","*.apk"),),font="Calibri 11")],
            [RoundedButton("View APK permissions",0.3,font="Calibri 11")],
            [gui.Text('Error message',key='_ERROR1_',visible=False,font="Calibri 11")],
            [gui.Text('ADB address:',font="Calibri 11")],
            [gui.Input(adbAddress,font="Calibri 11")],
            [RoundedButton('Install',0.3,font="Calibri 11"),RoundedButton('Installed apps',0.3,font="Calibri 11"),RoundedButton('Help',0.3,font="Calibri 11"),RoundedButton('About',0.3,font="Calibri 11")],
            [gui.Text("Error message",key='_ERROR2_',visible=False,font="Calibri 11")]]

    window = gui.Window('WSA Sideloader', layout,icon="icon.ico",debugger_enabled=False)

    while True:
        event, values = window.Read()
        if event is None:
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
        if event == "View APK permissions":
            source_filename = values[0]
            if os.path.exists(source_filename) == False:
                window['_ERROR1_'].Update("APK file not found")
                window["_ERROR1_"].Update(visible=True)
            elif source_filename.endswith(".apk") == False:
                window['_ERROR1_'].Update("Only APK files are supported")
                window["_ERROR1_"].Update(visible=True)
            else:
                source_filename = values[0]
                window.Hide()
                gui.popup_scrolled(os.popen('cmd /c "aapt d permissions "'+source_filename+'""').read(),size=(100,10),icon="icon.ico",title="APK permissions")
                window.UnHide()
        if event == "Installed apps": # Launch apps list of com.android.settings
            config.set('Application','adbAddress',values[1])
            with open(configpath, 'w') as configfile:
                config.write(configfile)
            autostart = os.popen('cmd /c "tasklist"')
            startoutput = str(autostart.readlines())
            if "WsaClient.exe" not in startoutput:
                startWSA(window)
            else:
                try:
                    window['_ERROR2_'].Update("Loading installed apps...")
                    window["_ERROR2_"].Update(visible=True)
                    address = values[1]
                    address = address.replace(" ", "")
                    adbRunning = True
                    command = os.popen('cmd /c "cd platform-tools & adb connect '+address+' & adb -s '+address+' shell am start -n "com.android.settings/.applications.ManageApplications""')
                    output = command.readlines()
                    check = str(output[len(output)-1])
                    if check.startswith("Starting: Intent { cmp=com.android.settings/.applications.ManageApplications }"):
                        window["_ERROR2_"].Update(visible=False)
                    else:
                        window['_ERROR2_'].Update("Please check that WSA is running and the correct ADB address\nhas been entered.\nRestart your computer if you continue to see this error.")
                        window["_ERROR2_"].Update(visible=True)
                except IndexError:
                    window['_ERROR2_'].Update("ADB address cannot be empty")
                    window["_ERROR2_"].Update(visible=True)
        if event == "Install":
            config.set('Application','adbAddress',values[1])
            with open(configpath, 'w') as configfile:
                config.write(configfile)
            source_filename = values[0]
            address = values[1]
            address = address.replace(" ", "")
            if source_filename == "":
                window['_ERROR2_'].Update("Please select an APK file.")
                window["_ERROR2_"].Update(visible=True)
            elif exists(source_filename) == False:
                window['_ERROR2_'].Update("File not found")
                window["_ERROR2_"].Update(visible=True)
            elif source_filename.endswith(".apk") == False:
                window['_ERROR2_'].Update("Only APK files are supported")
                window["_ERROR2_"].Update(visible=True)
            else:
                if address == "":
                    window['_ERROR2_'].Update("ADB address cannot be empty")
                    window["_ERROR2_"].Update(visible=True)
                else:
                    autostart = os.popen('cmd /c "tasklist"')
                    startoutput = str(autostart.readlines())
                    if "WsaClient.exe" in startoutput:
                        break
                    else:
                        startWSA(window)
        if event == "Help":
            window.Hide()
            helpLayout = [[gui.Text("This program is used to install APK files on Windows Subsystem for Android. Before using WSA Sideloader, make sure you:\n1. Installed Windows Subsystem for Android\n2. Enabled developer mode (open Windows Subsystem for Android Settings which can be found in your start menu and enable developer mode)\nWSA Sideloader also integrates with File Explorer and other supported programs, allowing APKs to be installed by just (double) clicking the file.\nFor more information and support, visit the GitHub page.",font=("Calibri",11))],[RoundedButton("Back",0.3,font="Calibri 11"),RoundedButton("GitHub",0.3,font="Calibri 11"),RoundedButton("Compatible apps",0.3,font="Calibri 11")]]
            helpWindow = gui.Window('Help',helpLayout,icon="icon.ico",debugger_enabled=False)
            while True:
                event,values = helpWindow.Read()
                if event is None:
                    if adbRunning == True:
                        os.popen('cmd /c "cd platform-tools & adb kill-server"')
                    sys.exit(0)
                elif event == "Back":
                    helpWindow.Close()
                    window.UnHide()
                    break
                elif event == "GitHub":
                    webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader",2)
                elif event == "Compatible apps":
                    webbrowser.open("https://github.com/riverar/wsa-app-compatibility",2)
        if event == "About":
            window.Hide()
            abtLayout = [[gui.Text('WSA Sideloader is a tool that is used to easily install APK files on Windows Subsystem for Android.\nThe program has been designed with simplicity and ease of use in mind.',font="Calibri 11")],[gui.Text("Application version: "+version,font="Calibri 11")],[gui.Text("Downloaded from: "+installsource,font="Calibri 11")],[RoundedButton("Back",0.3,font="Calibri 11"),RoundedButton("GitHub",0.3,font="Calibri 11")]]
            abtWindow = gui.Window('About',abtLayout,icon="icon.ico",debugger_enabled=False)
            while True:
                event,values = abtWindow.Read()
                if event is None:
                    if adbRunning == True:
                        os.popen('cmd /c "cd platform-tools & adb kill-server"')
                    sys.exit(0)
                elif event == "Back":
                    abtWindow.Close()
                    window.UnHide()
                    break
                elif event == "GitHub":
                    webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader",2)

    window.Close()

    layout = [[gui.Text('Installing application, please wait...',font=("Calibri",11))]]
    window = gui.Window('Please wait...', layout,no_titlebar=True,keep_on_top=True,debugger_enabled=False)
    event, values = window.Read(timeout=0)
    adbRunning = True
    command = os.popen('cmd /c "cd platform-tools & adb connect '+address+' & adb -s '+address+' install "'+source_filename+'""') # Command to install APK
    output = command.readlines()
    check = str(output[len(output)-1])
    window.Close()
    
    # Check if apk installed successfully
    if check.startswith("Success"):
        layout = [[gui.Text('The application has been successfully installed.',font=("Calibri",11))],
                [RoundedButton("Open app",0.3,font="Calibri 11"),RoundedButton("Install another APK",0.3,font="Calibri 11")]]
        window = gui.Window('Information', layout,icon="icon.ico",debugger_enabled=False)

        event, values = window.Read()
        if event == "Open app":
            getpackage = os.popen('cmd /c "aapt d permissions "'+source_filename+'""')
            pkgoutput = getpackage.readlines()
            pkgname = str(pkgoutput[0])
            webbrowser.open("wsa://"+pkgname[9:],2)
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
        elif event == "Install another APK":
            window.Close()
            main()
        else:
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
    else:
        layout = [[gui.Text('WSA Sideloader could not install the application. Please check that:\nThe APK file is valid\nWSA is running\nDev mode is enabled and the correct address has been entered\nIf you continue to see this error, restart your computer and try again.',font=("Calibri",11))],
                [RoundedButton("OK",0.3,font="Calibri 11"),RoundedButton("Report a bug",0.3,font="Calibri 11")]]
        window = gui.Window('Error', layout,icon="icon.ico",debugger_enabled=False)

        event, values = window.Read()
        if event == "OK":
            window.Close()
            main()
        elif event == "Report a bug": # Open WSA Sideloader issues page
            window.Close()
            webbrowser.open("https://github.com/infinitepower18/WSA-Sideloader/issues",2)
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)
        else:
            if adbRunning == True:
                os.popen('cmd /c "cd platform-tools & adb kill-server"')
            sys.exit(0)

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    if len(sys.argv) >1:
        startgit(sys.argv[1])
    else:
        startgit()
