; Um auszuführen: python .\mpa.py && python .\asm.py

#bankdef ram
{
    #addr 0x0000
    #size 0xFFFF
    #outp 8 * 0x10000 ; Ram nach den Instructions, wird später in asm.py aufgeteilt
}

#bankdef instructions
{
    #addr 0x0000
    #size 0xFFFF
    #outp 8 * 0x0
}

#subruledef register
{
    A => 0b00
    B => 0b01
    C => 0b10
    D => 0b11
}

#subruledef port ; Input Ports: P1 = 0-6 Ascii Logisim Tastatur 7 Bit 0, P2 = Buchstabe verfügbar FF wenn Buchstabe hingeschrieben wurde, also loop bis Buchstabe da und dann erst lesen
{                ; Output Ports: P1 = 8 bit 7 Segment Display mit Punkt. 0000 0001 für A, 0000 0010 für B, 0000 0100 für C, 0000 1000 für D, 0001 0000 für E, 0010 0000 für F, 0100 0000 für G, 1000 0000 für H (Punkt) oder kombination davon um die Buchstaben zu schreiben
                ; P2 = 0 bit für Tastatur löschen, 1 bit für Display clock. Für die löschung ungültiger zeichen.
    P1 => 0b00
    P2 => 0b01
    P3 => 0b10
    P4 => 0b11
}

#subruledef cc
{
    u => 0b00
    ne => 0b01
    e => 0b10
    x => 0b11
}

#subruledef cccc ; u,ne,b,be,a,ae,l,le,g,ge,o,no,s,ns,e,x
                ; unbedingt, not equal, below, below or equal, above, above or equal, less, less or equal, greater, greater or equal, overflow, no overflow, signum, no signum, equal, niemals
                ; https://www.intel.com/content/www/us/en/develop/download/intel-64-and-ia-32-architectures-sdm-combined-volumes-2a-2b-2c-and-2d-instruction-set-reference-a-z.html
{
    u => 0b0000
    ne => 0b0001
    b => 0b0010
    be => 0b0011
    a => 0b0100
    ae => 0b0101
    l => 0b0110
    le => 0b0111
    g => 0b1000
    ge => 0b1001
    o => 0b1010
    no => 0b1011
    s => 0b1100
    ns => 0b1101
    e => 0b1110
    x => 0b1111
}

;4 bit opn 0001 mov, 0010 add, etc. und dann 2x2bit or 1x4bit für die Register, conditions und/oder dannach ein immediate aus Label oder direkt geschrieben
#ruledef 
{
    mov {r1: register} {r2: register} => r2 @ r1 @ 0b0001
    add {r1: register} {r2: register} => r2 @ r1 @ 0b0010
    sub {r1: register} {r2: register} => r2 @ r1 @ 0b0011
    nand {r1: register} {r2: register} => r2 @ r1 @ 0b0100
    shift {r1: register} {r2: register} => r2 @ r1 @ 0b0101
    cmp {r1: register} {r2: register} => r2 @ r1 @ 0b0110
    store {r1: register} {r2: register} => r2 @ r1 @ 0b0111 ; speichere wert r2 in ram adresse r1 nicht immediate
    load {r1: register} {r2: register} => r2 @ r1 @ 0b1000 ; lade wert r2 ins ram adresse nicht immediate
    const {cc: cc} {r1: register} {imm: u8} => r1 @ cc @ 0b1001 @ imm
    jmp {cccc: cccc} {immh: u8} {imml: u8} => cccc @ 0b1010 @ immh @ imml
    jmp {cccc: cccc} {imm: u16} => cccc @ 0b1010 @ imm ; für label jumps
    out {port: port} {r1: register} => r1 @ port @ 0b1011 ; output r1 an port 1-4
    in {port: port} {r1: register} => r1 @ port @ 0b1100 ; input port 1-4 an register r1


}


; Aktuelles program ist eine Schreibmaschine, welches eingabe von einer Tastatur einliest und dann diesen auf einen 7-Segment Display ausgibt.

const u B 0x01      ; Wert 0x01 für Verfügbarkeit von Zeichen, muss bei jedem zurückspringen in diesen loop 1 sein.
check_available:
in P2 A             
cmp A B             ; Prüfe, ob Zeichen verfügbar
jmp ne check_available ; Springe zurück, falls Zeichen nicht verfügbar

in P1 D             ; Lade ASCII-Wert in D

; Prüfen ob Punkt
const u B "."
cmp D B
jmp ne search_match

; Shift punktPuffer um 1. Dadurch wird sich der letzte Bit immer abwechseln
const u D punktPuffer
load C D           ; punktpuffer in C laden
const u B 0b00010001 ; Shift-Spezifische Befehle, Rotierend nach links um 1
shift C B
store D C          ; Shifted punktpuffer wieder speichern
out P3 C           ; Punkt darstellen

; Punkt aus dem keyboard löschen
const u C 0x01
out P2 C
const u C 0x00
out P2 C

const u B 0x01 ; RESET B zu 0x01, damit überprüft werden kann, ob ein Buchstabe eingegeben wurde.
jmp u check_available


search_match:       ;Suche nach passendem ASCII-Wert
const u A lookup_table
const u C 0x02      ; Schrittweite um 2 Springen ASCII zu ASCII vorbereiten


search_loop:
load B A            ; Lade ASCII-Wert aus Speicher in B
cmp B D             ; Vergleiche Speicherwert mit Tastatureingabe
jmp e found_match   ; Falls Übereinstimmung, springe zu found_match
add A C             ; Erhöhe Adresse um 2

const u B table_end ; Falls am Ende der Tabelle ist der ASCII code nicht enthalten und deswegen ungültig
cmp A B
jmp ge clearIncorrect
jmp u search_loop  ; Wiederhole Suche falls nicht am Ende und noch nicht gefunden

found_match:        
const u C 0x00
add A C             ; Erhöhe Adresse um 1, um den 7-Segment-Wert zu bekommen 
load B A
out P1 B            ; Ausgabe des 7-Segment-Werts an P1 (Display)


; reset punktPuffer damit der Punkt nur einmal gesetzt wird
const u D punktPuffer
const u C 0b10101010
store D C


; Keyboard und Display clocken
const u C 0x03
out P2 C 
const u C 0x00     ; Reset clock
out P2 C
out P3 C

const u B 0x01
jmp u check_available

clearIncorrect:
; Leerzeichen einfügen
const u C 0x00
out P1 C
const u C 0x03
; Falschen Buchstaben löschen und display clocken
out P2 C
const u C 0x00 
out P2 C
const u B 0x01
jmp u check_available




#bank ram
; ASCII - 7 Segment Display - ASCII - 7 Segment Display - ...
lookup_table:
#d8 "a", 0x5F, "b", 0x7C, "c", 0x58, "d", 0x5E, "e", 0x7B, "f", 0x71, "g", 0x6F, "h", 0x74, "i", 0x10, "j", 0x0C, "k", 0x75, "l", 0x30, "m", 0x14, "n", 0x54, "o", 0x5C, "p", 0x73, "q", 0x67, "r", 0x50, "s", 0x6D, "t", 0x78, "u", 0x1C, "v", 0x1C, "w", 0x14, "x", 0x76, "y", 0x6E, "z", 0x5B
#res 3
#d8 "0", 0x3F, "1", 0x06, "2", 0x5B, "3", 0x4F, "4", 0x66, "5", 0x6D, "6", 0x7D, "7", 0x07, "8", 0x7F, "9", 0x6F, "[", 0x39, "]", 0x0F, "{", 0x46, "}", 0x70, "=", 0x48
#res 3
#d8 "!", 0x86, "?", 0xD3, "@", 0x5F, "-", 0x40
#res 2
#d8 "-"
table_end:
#d8 0x40
punktPuffer:
#d8 0b10101010 ; Abwechselnde Bits für das toggeln
