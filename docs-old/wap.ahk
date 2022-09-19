; An AutoHotKey script to perform the wap demo gif animation. https://www.autohotkey.com/
; Makes it consistent, repeatable, error-free, followable with the eyes
; Ran on windows with powershell and alacritty
; Captured with ScreenToGif https://www.screentogif.com/

F9::
    SetKeyDelay, 100, 0
    Send, wap quickstart MyAddon{Enter}
    Sleep, 3000
    Send, {Enter} ; default addon name
    Sleep, 1000
    Send, Thrall{Enter} ; author name
    Sleep, 1000
    Send, A neat new addon built with wap{!}{Enter} ; description
    Sleep, 1000
    Send, y{Enter} ; yes to retail
    Sleep, 1000
    Send, n{Enter} ; no to classic
    Sleep, 1000
    Send, y{Enter} ; yes to curseforge
    Sleep, 1000
    Send, 441390{Enter} ; project id
    Sleep, 1000
    Send, https://www.curseforge.com/wow/addons/myaddon{Enter} ; addon url
    Sleep, 3000
    Send, cd "MyAddon"{Enter}
    Sleep, 3000
    Send, wap build{Enter}
    Sleep, 3000
    Send, wap dev-install --wow-addons-path "C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"{Enter}
    Sleep, 3000
    Send, wap upload --addon-version "dev" --curseforge-token "71f2fcc8-7ee9-4173-880f-21b48f1b8059"{Enter}
    Sleep, 7000
