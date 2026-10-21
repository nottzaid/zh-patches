# Heal-wait check for JetAIUpdate::update (Game.dat, Steam build Feb 20 2025), placed at 0x942f10.
# Entered from 0x6540b4, the start of "else if (HAS_PENDING_COMMAND && state != RELOAD_AMMO)"'s body.
# Live here: esi = this+0x14 (m_flags at [esi+0x308]), ebx = jet Object*, ebp = ParkingPlace interface or 0.
# Extra condition: a parked jet (no ALLOW_AIR_LOCO) at a live airfield keeps its pending command until
# getHealth() == getMaxHealth(), the same test the helicopter branch above uses.
.intel_syntax noprefix
.globl _start
_start:
    test byte ptr [esi+0x308], 2        # ALLOW_AIR_LOCO: airborne, nothing to heal for
    jnz resume
    test ebp, ebp                       # no airfield, no healing
    jz resume
    mov ecx, [ebx+0x174]                # jet->getBodyModule()
    push ecx                            # [esp+4] = body
    push ecx                            # [esp]   = float scratch
    mov eax, [ecx]
    call [eax+0xc]                      # st0 = body->getHealth()
    fstp dword ptr [esp]
    mov ecx, [esp+4]
    mov eax, [ecx]
    call [eax+0x10]                     # st0 = body->getMaxHealth()
    fcomp dword ptr [esp]
    fnstsw ax
    add esp, 8
    test ah, 0x40                       # C3: equal
    jz wait
resume:
    push 2                              # the 8 bytes overwritten at 0x6540b4
    push 0
    lea ecx, [esp+0x60]
    jmp 0x6540bc
wait:
    jmp 0x654165                        # as if the pending-command condition were false
