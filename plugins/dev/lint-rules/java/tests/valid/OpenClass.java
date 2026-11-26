package app;
public class OpenClass {
    private final int limit = 10;
    public final int limit() { return limit; }
}
record Point(int x, int y) { }
sealed interface State permits On, Off { }
record On() implements State { }
record Off() implements State { }
@SuppressWarnings("final")
class Annotated { }
