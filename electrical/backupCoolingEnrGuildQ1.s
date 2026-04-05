* Back up Cooling Fan Management

    TTL backupCoolingEnrGuildQ1
    AREA Program, CODE, READONLY
    ENTRY

Main
            LDRB    R0, Value

            ;Extracts ovr, temp, ac, racks using bitwise operations

            AND     R1, R0, #&80     ;bit mask for ovr, 10000000   
            MOV     R1, R1, LSR #7   ;right shift by 7 bits
            STRB    R1, ovr
            
            AND     R1, R0, #&60     ;bit mask for temp, 01100000   
            MOV     R1, R1, LSR #5   ;right shift by 5 bits
            STRB    R1, temp
            
            AND     R1, R0, #&18     ;bit mask for ac, 00011000   
            MOV     R1, R1, LSR #3   ;right shift by 3 bits
            STRB    R1, ac

            AND     R1, R0, #&7      ;bit mask for racks, 00000111   
            STRB    R1, racks

            ;Evaluates trigger conditions and goes to turnOn if true, done if false    

            LDRB    R1, ovr
            CMP     R1, #&1
            BEQ     turnOn


            LDRB    R1, temp
            CMP     R1, #&3
            BEQ     turnOn


            LDRB    R1, racks
            CMP     R1, #&4
            BLE     done

            ;BGT, this executes:

            LDRB    R1, ac
            CMP     R1, #&0
            BNE     done

            ;flow only reaches here if both racks>4 and ac = 0
            B       turnOn


            ;Stores result in R1

turnOn:
            MOV    R1, #&1         ;Stores result as 1 if conditions are met
            B end

done:
            MOV    R1, #&0         ;Stores result as 0 if conditions are not met            

end:
            SWI     &11


Value       DCB     0               ;Value
            ALIGN
ovr         DCB     0               ;space to store override bit
            ALIGN
temp        DCB     0               ;space to store temperature bits
            ALIGN
ac          DCB     0               ;space to store ac state
            ALIGN
racks       DCB     0               ;space to store racks bits

            END