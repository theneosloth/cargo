# CargoExport
Export utilities for mediawiki cargo tables

# Example
```
> from sites.dreamcancel import KOFXV
> from sites.dustloop import GGACR
> KOFXV().get_move("Kyo Kusanagi", "qcf+C")
[MoveData_KOFXV(chara='Kyo Kusanagi', moveId='kyo_qcf+cd', orderId=None, input='qcf+CD', name='ShatterStrike', header=None, version=None, images=['XV_kyo_236cd_ima.png'], hitboxes=['XV_placeholder.png'], damage=75, guard=['[[The_King_of_Fighters_XV/Defense#Mid|Mid]]'], cancel=None, startup=15, active=6, recovery=None, hitadv='Crumple (Ground Hit) / Wall Bounce (Air hit)', blockadv=-10, invul='Armor: 4 to 14 (11 frames)', stun=0, guardDamage=200)]
> GGACR().get_move("Sol Badguy", "j.D")
[MoveData_GGACR(chara='Sol Badguy', name=None, input='j.D', damage=40, guard='High/Air', startup=9, active=7, recovery='10+5 after landing', onBlock=None, onHit=None, level=4, images=['GGAC_Sol_jD.png'], hitboxes=['GGXXACPR_Sol_jD-1-Hitbox.png', 'GGXXACPR_Sol_jD-2-Hitbox.png'], notes=['Blows back opponent on normal hit', 'Wall bounces opponent on CH (untechable for 54F)'], caption=['&amp;#32;'], type='normal', gbp=11, gbm=6, tension=3.84, prorate='90%', invuln=None, cancel='SJR', blockstun=16, groundHit='Launch', airHit=27, hitstop=14)]

```
