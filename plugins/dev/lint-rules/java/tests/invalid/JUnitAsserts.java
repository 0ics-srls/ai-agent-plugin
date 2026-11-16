package app;
public class JUnitAsserts {
    void t(int x, boolean b, Object o) {
        assertEquals(1, x);
        assertTrue(b);
        assertNotNull(o);
    }
}
