These test files assume the following:

1. You will number your registers as $0, $1, $2, etc.
2. Register $0 is hardwired to zero.
3. The first instruction will be at address (line) zero.
4. Branch instructions will use offsets from PC+1 as the third argument (labels are an upgrade).
5. Jump instructions j and jal will use addresses as their arguments (again, labels are an upgrade).
6. All registers contain zero at the start unless otherwise noted.

If your processor requires you to rewrite any of these tests, you MUST turn in your new test files (.asm and .hex) on Nexus as part of your project submission.