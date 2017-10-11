#! /usr/bin/env python3.5

import inkpy as ink

s = ink.Story("test.json")

while s.can_continue:
    print(s.continue_())
