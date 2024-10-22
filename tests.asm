; Verschieden Programme um einzelne Funktionen zu testen

; funktioniert loop bis overflow
; const u A 0x1

; main:
; add A A
; jmp no main


; Speichern im RAM
; const u A 0x1
; const u D 0x3
; store D A
; load B D
; 


; Lable Tests
; const u b 0xFF
; const u c 0x00
; loop: 
; in P1 a
; out P1 a
; out P2 B
; out P2 C
; jmp u loop

; out P2 C




; const u A location 
; load B A ; B sollte "s" sein


; Ram Labels test mit Offset
; #bank ram
; #d "abcd"
; location:
; #d "s"



; const u C 0x00 
; const u D 0x01

; ; Test if 0 is 0
; cmp C D
; jmp ne error
; const u A 0x41

; #d 0x00, 0x00, 0x00, 0x00


; error:
; jmp u error

