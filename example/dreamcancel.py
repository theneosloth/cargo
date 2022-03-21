from cargo.cargo import Cargo, cargo_export

valid_fields = ["chara", "moveId", "orderId", "input","name", "header", "version", "images", "hitboxes", "damage", "guard", "cancel", "startup", "active", "recovery", "hitadv", "blockadv", "invul", "stun", "guardDamage"]

field_param = ",".join(valid_fields)

cargo = Cargo()
c = cargo_export(cargo, {"tables": "MoveData_KOFXV", "fields": field_param})

print(c)
