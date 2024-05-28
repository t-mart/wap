; An AutoHotKey2 script to perform the wap demo gif animation. https://www.autohotkey.com/
; Makes it consistent, repeatable, error-free, followable with the eyes
; Capture with ScreenToGif https://www.screentogif.com/

TypeCommand(text, delay := 1500)
{
    SendText text
    Send "{Enter}"
    Sleep delay
}

; press F9 with terminal focus to start
F9::
{
    SendMode "Event"
    SetKeyDelay 100, 0
    TypeCommand("wap new-project", 3000)  ; start questions
    TypeCommand("MyAddon")  ; package/addon name
    TypeCommand("")  ; default author name
    TypeCommand("A neat new addon built with wap!")  ; description
    TypeCommand("")  ; default version
    TypeCommand("y")  ; yes to retail
    TypeCommand("y")  ; yes to classic
    TypeCommand("y")  ; yes to vanilla
    TypeCommand("y")  ; yes to publish
    TypeCommand("441390")  ; project id
    TypeCommand("my-addon")  ; project slug
    TypeCommand("y")  ; yes to all ok
    TypeCommand('cd "MyAddon"')  ; cd
    TypeCommand("wap build --link")  ; build
    TypeCommand('wap publish --release-type beta --curseforge-token "af6282fd-4c9b-471d-b55d-01a9bbb3f43d"', 5000)  ; upload
}

F8:: Reload
