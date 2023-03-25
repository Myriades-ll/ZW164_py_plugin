# 2.2.0 -

- Added: HTML page; in progress

---

## 2.1.1 - 2023/03/25

- Fixed: bug in http header response analyse

## 2.1.0 - 2022/12/29

- Added: [todo list](/docs/todo.md)
- Added: device added to location/plan automatically
- Added: location/plan autocreation
- Added: mark device as used @ device creation
- Added: remove leading hardware name in front of device name @ device creation
- Added: some Domoticz error logs, just in case of
- Cleaned: some [PEP8][def_PEP8] misspelling
- Fixed: makes some methods faster
- Fixed: minor bug, wrong `nValue` when a command was thrown to hardware
- Fixed: some unpythonic values
- Removed: comments in README.md

## 2.0.0 - 2022/12/17

- Full rewrite, every SoundSwitch; that embed the 0x79|121 command class; will should be functional

## 1.0.0 - 2022/11/26

- First release, it makes the AEOTEC ZW164 functional

[def_PEP8]: https://peps.python.org/pep-0008/
