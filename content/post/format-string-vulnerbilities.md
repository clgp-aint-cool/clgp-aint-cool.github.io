---
title: 'Format String Vulnerbilities'
author: clgp
date: '2025-11-16T00:50:33+07:00'
categories:
  - ctf 
tags:
  - bwn
---

## fmtstr_payload() in pwntools

```bash
from pwn import *

payload = fmtstr_payload(offset, writes, numbwritten='byte')

```

**+offset is the stack offset of where you want to do the payload** 

**+writes is a pair value { address_to_write_to: value_to_write }**

**+numbwritten (optional) is the number of byte that have been printed before the 
payload is processed**

## Example

Let's say you are doing a CTF challenge where:

You found a format string vulnerability.

You used a debugger (like GDB) and found that your payload starts at offset 7.

You want to overwrite a variable called *is_admin* located at address
0x0804a02c with the value 1 to get admin privileges.


```python
from pwn import *

# The address of the 'is_admin' variable
admin_variable_address = 0x0804a02c

# The value we want to write (1)
new_value = 1

# The stack offset we found
offset = 7

# Generate the payload
payload = fmtstr_payload(offset, {admin_variable_address: new_value})


# You would then send this payload to the vulnerable program
# p = process('./vulnerable_program')
# p.sendline(payload)
```

When the vulnerable program executes printf(payload),
this specially crafted string will cause it to write the value 1 into the address 0x0804a02c.
fmtstr_payload() automatically handles all the %n, %hn, %hhn specifiers and padding (%...c)
to get the exact value you want written to the exact address.

## Why this function *fmtstr_payload()* actually help 

This function help yout to write payload which control
exactly what value gets written to which address.

##  Why This Is a Lifesaver: The Manual Method

**Our Goal:** Write the 4-byte value **`0xDEADBEEF`** to the address **`0x12345678`**.

> **Assumptions:**
> * We are on a little-endian system (most x86/ARM CPUs).
> * This means `0xDEADBEEF` at `0x12345678` is stored in memory as:
>     * `0xEF` at `0x1234567B`
>     * `0xBE` at `0x1234567A`
>     * `0xAD` at `0x12345679`
>     * `0xDE` at `0x12345678`
> * We will use `%hhn` (which writes 1 byte) for our writes.
> * The `printf` byte counter (which `%hhn` uses) starts at `0`.

---

### Step 0: The *Sort*

The `printf` counter can only **increase**. We can't write `222` bytes and then write `173` bytes, because the counter would already be past `173`.

Therefore, we **must sort our writes from the lowest byte value to the highest**:

1.  Write `0xAD` (`173`) -> to address `0x12345679`
2.  Write `0xBE` (`190`) -> to address `0x1234567A`
3.  Write `0xDE` (`222`) -> to address `0x12345678`
4.  Write `0xEF` (`239`) -> to address `0x1234567B`

Our payload will perform 4 writes in this specific order.

---

### Step 1: Write the value 173 (0xAD)

* **Goal:** Write `173` to `0x12345679`.
* **Current Counter:** `0`
* **Action:** We need the counter to become `173`. We do this by printing `173` padding characters.
* **Payload Part:** `%173c...` (followed by a `%...$hhn` specifier pointing to `0x12345679`)
* **Result:**
    * `printf` prints `173` characters.
    * The counter increases from `0` to **`173`**.
    * The `%hhn` triggers and writes the value `173` (which is `0xAD`) to the address `0x12345679`.

### Step 2: Write the value 190 (0xBE)

* **Goal:** Write `190` to `0x1234567A`.
* **Current Counter:** `173`
* **Action:** We need the counter to become `190`. It's already at `173`, so we only need to print an additional **`190 - 173 = 17`** characters.
* **Payload Part:** `%17c...` (followed by a `%...$hhn` specifier pointing to `0x1234567A`)
* **Result:**
    * `printf` prints an additional `17` characters.
    * The counter increases from `173` to **`190`**.
    * The `%hhn` triggers and writes the value `190` (which is `0xBE`) to the address `0x1234567A`.

### Step 3: Write the value 222 (0xDE)

* **Goal:** Write `222` to `0x12345678`.
* **Current Counter:** `190`
* **Action:** We need the counter to become `222`. We need to print an additional **`222 - 190 = 32`** characters.
* **Payload Part:** `%32c...` (followed by a `%...$hhn` specifier pointing to `0x12345678`)
* **Result:**
    * `printf` prints an additional `32` characters.
    * The counter increases from `190` to **`222`**.
    * The `%hhn` triggers and writes the value `222` (which is `0xDE`) to the address `0x12345678`.

### Step 4: Write the value 239 (0xEF)

* **Goal:** Write `239` to `0x1234567B`.
* **Current Counter:** `222`
* **Action:** We need the counter to become `239`. We need to print an additional **`239 - 222 = 17`** characters.
* **Payload Part:** `%17c...` (followed by a `%...$hhn` specifier pointing to `0x1234567B`)
* **Result:**
    * `printf` prints an additional `17` characters.
    * The counter increases from `222` to **`239`**.
    * The `%hhn` triggers and writes the value `239` (which is `0xEF`) to the address `0x1D234567B`.

---

### Summary

After 4 complex, ordered steps, we have performed 4 writes:

* `0x12345678` now contains `0xDE`
* `0x12345679` now contains `0xAD`
* `0x1234567A` now contains `0xBE`
* `0x1234567B` now contains `0xEF`

All 4 of these bytes combine to form the value **`0xDEADBEEF`** at the address `0x12345678`.

This is the extremely complex logic (sorting, calculating differences, handling padding, and managing addresses) that `fmtstr_payload()` automates for you in a single, clean line of code.
